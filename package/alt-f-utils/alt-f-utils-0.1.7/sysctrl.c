/* Copyright Joao Cardoso, 2009-2016
 * Licence: GPLv2 
 *
 * Some code stolen from fonz fanctl and dns323-utils, 
 * other from Mark Lord <mlord@pobox.com> hdparm
 * other from hd-idle, https://sourceforge.net/projects/hd-idle/
 *
 * To be used with Alt-F
 * 
 * -Provides fan control, hdd sleep detection, RAID status, power and reset button handling:
 * -sends SCSI sleep command to attached USB disks (that hdparm can't put at sleep)
 * -Reboots when power button pressed between 3 and 6 seconds (right led flashing)
 * -poweroff when power button pressed between 6 and 9 seconds (left led flashing)
 *  runs user suplied scripts on any of those events
 *  or when reset button momentary pressed (both left flashing)
 * -unmounts all USB mounted filesystems when the back buton is pressed less then 10 sec
 * -Starts telnet on port 26, no password, is back button is pressed
 *  more than 10 but less than 20  seconds
 * -clears flash-saved settings and performs a reboot if back button is pressed
 *   more than 20 seconds.
 * -configurable through /etc/sysctrl.conf
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/types.h>
#include <sys/inotify.h>
#include <sys/stat.h>
#include <signal.h>
#include <fcntl.h>
#include <syslog.h>
#include <sys/swap.h>
#include <linux/hdreg.h>
#include <linux/input.h>
#include <ctype.h>
#include <libgen.h>
#include <math.h>
#include <time.h>


void check_board();

void fanctl(void);

void hdd_powercheck(int noleds);
int check_powermode(char *dev);
unsigned long dstat(char *dsk);
int md_stat(void);
int check_syserrlog();

int debounce();
int button(void);

void led_set(int which, char *mode);
int led_get(int which, char *mode);
void led_blink(int which, char *on, char *off);

void leds_on();
void leds_off();
void leds_blink();

void leds_proc();
void leds_set(int mode, int priority);

void syswrite(char *fname, char *value);

void back_button();
void reboot();
void poweroff();

int umountall();
int unswapall();
int killall();

void setup();
void mainloop();

int syserrorlog(char *str);
void logger(char *cmd);

char *checkfile(char *fname);
void check_other_daemon();
void exec_userscript(char *script, int timeout, char *script_arg);

void read_bay();
void read_misc();
void read_config();
void print_config();
void print_disks();

typedef struct {
	float hist_temp;
	int lo_fan, hi_fan, lo_temp, hi_temp, mail, recovery, fan_off_temp,
		max_fan_speed, warn_temp, crit_temp, fan_mode;
	char *warn_temp_command, *crit_temp_command,
		*front_button_command1, *front_button_command2, *back_button_command;
} args_t;

enum FanMode {FAN_AUTO = 0, FAN_ALWAYS_OFF, FAN_ALWAYS_SLOW , FAN_ALWAYS_FAST};

// configuration default values, overriden by configuration files
args_t args =
    { 2.0, 2000, 5000, 40, 50, 1, 1, 38, 6000, 52, 54, FAN_AUTO, NULL, "/usr/sbin/poweroff", NULL, NULL,
  NULL };

enum Board { DNS_323_A1, DNS_323_B1, DNS_323_C1, DNS_321_Ax, DNS_325_Ax, DNS_320_Ax, DNS_320_Bx, DNS_320L_Ax, DNS_327L_Ax};
int board;

enum Button { NO_BT=0, FRONT_BT, RESET_BT, USB_BT };
enum PwdValue { PWM_OFF = 0, PWM_LOW = 127, PWM_FAST = 255 };
enum RPMValue { RPM_OFF = 0, RPM_LOW = 3000, RPM_FAST = 6000 };

enum Led { left_led = 0, right_led, usb_led, power_led};
char *leds[] = { "/tmp/sys/left_led/", "/tmp/sys/right_led/", "/tmp/sys/usb_led/", "/tmp/sys/power_led/"};

#define NSLOTS 3
int nslots = NSLOTS;

enum Slot { left_dev = 0, right_dev, usb_dev};
typedef struct {
	char *dev;
	char *slot;
	unsigned long rdwr_cnt;
	time_t last_access;
	time_t spindow_time;
	int power_state;
} disk_t;

disk_t disks[NSLOTS];
int ndisks = 0;

char sys_pwm[] = "/tmp/sys/pwm1",
	sys_fan_input[] = "/tmp/sys/fan1_input",
	sys_temp_input[] = "/tmp/sys/temp1_input",
	sys_power_button[] = "/tmp/sys/power_button";

int fd_ev, wd_bay, wd_misc, wd_conf;

char syserrorfn[] = "/var/log/systemerror.log";
char fantemplog[] = "/var/log/fantemp.log";

#define SCRIPT_TIMEOUT 5

#define IDLE	0
#define REBOOT	3
#define HALT	6
#define ABORT	9

#define BUFSZ 256

void quit_handler() {
	syslog(LOG_INFO, "signaled to quit, quiting");
	exit(0);
}

void alarm_handler() {
}

void debug_handler() {
	print_config();
	print_disks();
}

void sighup_handler() {
	read_config();
	read_bay();
	read_misc();
}

void inotify_handler() {
	char ev_buffer[10*BUFSZ];

	int length = read(fd_ev, ev_buffer, 10*BUFSZ);
	if (length > 0) {
		int i = 0, miscf = 0, bayf = 0, conff = 0;
		struct inotify_event *ev;
		while(i < length) {
			ev = (struct inotify_event *) &ev_buffer[i];
			// syslog(LOG_INFO, "inotify len=%d name=%s wd=%d cookie=%d mask=%x i=%d",
			//	   length, ev->name, ev->wd, ev->cookie, ev->mask, i);

			if (ev->wd == wd_misc) {
				if (ev->mask == IN_IGNORED) /* 'sed -i' deletes file */
					wd_misc = inotify_add_watch(fd_ev, "/etc/misc.conf", IN_MODIFY | IN_MOVE | IN_IGNORED);
				miscf = 1;
			} else if (ev->wd == wd_bay) {
				if (ev->mask == IN_IGNORED)
					wd_bay = inotify_add_watch(fd_ev, "/etc/bay", IN_MODIFY | IN_MOVE | IN_IGNORED);
				bayf = 1;
			} else if (ev->wd == wd_conf) {
				if (ev->mask == IN_IGNORED)
					wd_conf = inotify_add_watch(fd_ev, "/etc/sysctrl.conf", IN_MODIFY | IN_MOVE | IN_IGNORED);
				conff = 1;
			}
			i += (sizeof (struct inotify_event)) + ev->len;
		}
		if (bayf)
			read_bay();
		if (miscf)
			read_misc();
		if (conff)
			read_config();
	}
}

int main(int argc, char *argv[]) {
	int i;

	check_board();
	
	/* daemonize: fork, cd /, setsid, close io */
	daemon(0, 0);
	check_other_daemon();

	struct sigaction new;
	sigset_t smask;

	sigemptyset(&smask);
	new.sa_mask = smask;
	new.sa_flags = 0;

	new.sa_handler = quit_handler;
	sigaction(SIGTERM, &new, NULL);
	
	// avoid zombie processes due to user scripts
	new.sa_handler = SIG_IGN;
	sigaction(SIGCHLD, &new, NULL);

	// timeout for user scripts
	new.sa_handler = alarm_handler;
	sigaction(SIGALRM, &new, NULL);

	// reread configuration files
	new.sa_handler = sighup_handler;
	sigaction(SIGHUP, &new, NULL);
	
	// dump configs
	new.sa_handler = debug_handler;
	sigaction(SIGUSR1, &new, NULL);
	
	// inotify actions (/etc/bay, /etc/misc.conf, /etc/sysctrl.conf changes)
	new.sa_handler = inotify_handler;
	sigaction(SIGIO, &new, NULL);

	/* log messages with syslog and write to /dev/console */
	openlog("sysctrl", LOG_CONS , LOG_DAEMON);
	syslog(LOG_INFO, "Starting");

	/* register inotify for changes in config files */
	fd_ev = inotify_init();
	fcntl(fd_ev, F_SETFL, fcntl(fd_ev, F_GETFL, 0) | O_ASYNC | O_NONBLOCK);
	fcntl(fd_ev, F_SETOWN, getpid());
		  
	wd_misc = inotify_add_watch(fd_ev, "/etc/misc.conf", IN_MODIFY | IN_MOVE | IN_IGNORED);
	wd_bay = inotify_add_watch(fd_ev, "/etc/bay", IN_MODIFY | IN_MOVE | IN_IGNORED);
	wd_conf = inotify_add_watch(fd_ev, "/etc/sysctrl.conf", IN_MODIFY | IN_MOVE | IN_IGNORED);

	for (i = 0; i < nslots; i++)
		disks[i].power_state = 1;
	
	read_bay();
	read_misc();
	read_config();
	
	print_config();
	print_disks();

	/* do the actual work */
	mainloop();
	
	close(fd_ev);
	closelog();
	return 0;
}

void mainloop() {

	int bt, count = 0, state = IDLE;

	int powercheck_interval = 5;
	int powercheck_count = powercheck_interval - 1;

	int fan_interval = 15;
	int fan_count = fan_interval - 1;
	
	/* block all signals mask */
	sigset_t set;
	sigfillset(&set);

	leds_off();

	while (1) {
		sigprocmask(SIG_BLOCK, &set, NULL); // block signal delivery (critical section)

		if ((fan_count++ % fan_interval) == 0)
			fanctl();

		bt = debounce();
		//syslog(LOG_INFO, "button %d ", bt);
		count++;

		if ((++powercheck_count % powercheck_interval) == 0 && bt == NO_BT) {
			//hdd_powercheck(md_stat(check_syserrlog()));
			hdd_powercheck(0);
			md_stat();
			check_syserrlog();
			leds_proc();
		}

		if (bt && state == IDLE)
			leds_off();

		if (bt == RESET_BT || bt == USB_BT) {
			back_button();
			continue;
		}

		switch (state) {
		case IDLE:
			if (bt == NO_BT) {
				count = 0;
			} else if (count == REBOOT) {
				state = REBOOT;
				led_blink(right_led, "250", "250");
			}
			break;

		case REBOOT:
			if (bt == NO_BT) {
				state = IDLE;
				count = 0;
				leds_off();
				reboot();
			} else if (count == HALT) {
				state = HALT;
				led_set(right_led, "0");
				led_blink(left_led, "250", "250");
			}
			break;

		case HALT:
			if (bt == NO_BT) {
				state = IDLE;
				count = 0;
				leds_off();
				poweroff();
			} else if (count == ABORT) {
				state = IDLE;
				count = 0;
				leds_off();
			}
			break;
		}
		sigprocmask(SIG_UNBLOCK, &set, NULL); // allow signal delivery
		sleep(1);
	}
	return;
}

void back_button() {
	time_t count = time(NULL);
	int bt;
	
	syslog(LOG_INFO, "Entering back_button");

	leds_blink();
	
	do {
		bt = debounce();
		usleep(200000);
	} while ( bt == RESET_BT || bt == USB_BT);

	count = time(NULL) - count;

	if (args.recovery && count > 20) // twenty seconds
		exec_userscript("/usr/sbin/recover", SCRIPT_TIMEOUT, "f"); // clear flash, reboot
	else if (args.recovery && count > 10) 	// ten seconds
		exec_userscript("/usr/sbin/recover", SCRIPT_TIMEOUT, "t"); // telnet port 26
	else if (args.back_button_command)
		exec_userscript(args.back_button_command, SCRIPT_TIMEOUT, NULL);
	else
		exec_userscript("/usr/bin/eject", SCRIPT_TIMEOUT, "usb");
	
	leds_off();
}

void reboot() {
	syslog(LOG_INFO, "Rebooting NOW");
	exec_userscript(args.front_button_command1, SCRIPT_TIMEOUT, NULL);
	execl("/sbin/reboot", "reboot", NULL);
}

void poweroff() {
	syslog(LOG_INFO, "Poweroff NOW");
	exec_userscript(args.front_button_command2, SCRIPT_TIMEOUT, NULL);
	execl("/usr/sbin/poweroff", "poweroff", NULL);
}

char *checkfile(char *fname) {
	struct stat buf;

	if (fname == NULL || strlen(fname) == 0)
		return NULL;

	if (stat(fname, &buf)) {
		syslog(LOG_INFO, "non accessible file \"%s\"", fname);
		return NULL;
	}

	if ((buf.st_uid != 0) ||	/* not owned by root */
	    (!(buf.st_mode & S_IXUSR)) ||	/* not executable */
	    (buf.st_mode & (S_IWGRP | S_IWOTH))) {	/* group and others has write access */
		syslog(LOG_INFO,
		       "file \"%s\" not owned by root, not executable or writable by non-root",
		       fname);
		return NULL;
	}

	return fname;
}

char *pop_sys(char *cmd, char *res) {
	FILE *f = popen(cmd, "r");
	if (f == NULL) {
		syslog(LOG_ERR, "error popen: %s", cmd);
		return NULL;
	}
	char *ret = fgets(res, 80, f);
	pclose(f);
	return ret;
}

#define WARNT "warning"
#define CRITT "CRITICAL"
void smail(char *type, int fan, float temp, int limit) {

	char host[80];
	pop_sys("/bin/hostname -f", host);
	
	char to[80];
	if (pop_sys("grep '^MAILTO' /etc/misc.conf | cut -d= -f2", to) == NULL) {
		syslog(LOG_ERR, "mail not configured");
		return;
	}
	
	char from[80];
	if (pop_sys("grep '^from' /etc/msmtprc | cut -f2", from) == NULL) {
		syslog(LOG_ERR, "mail not configured");
		return;
	}
	
	FILE *fo = popen("/usr/bin/msmtp --read-recipients", "w");
	if (fo == NULL) {
		syslog(LOG_ERR, "error sending mail");
		return;
	}
	fprintf(fo, "To: %s"
		"From: %s"
		"Subject: Alt-F System Control %s message\n\n"
		"This is a %s message from %s\n"
		"Fan speed=%d\nSystem Temperature=%.1f\nLimit Temperature=%d\n\n"
		"This message will not be sent again unless the situation normalizes and reappears afterwards.\n", to, from, type, type, host, fan, temp, limit);
	fclose(fo);
}

void exec_userscript(char *script, int timeout, char *arg) {
	if (script == NULL || strlen(script) == 0)
		return;

	syslog(LOG_INFO, "executing user script \"%s\"", script);

	pid_t pid = fork();
	if (pid == 0) {
		execl(script, script, arg, NULL);
		syslog(LOG_ERR, "exec of user script \"%s\" failed", script);
		// exit(1);
	} else if (pid > 0) {
		alarm(timeout);
		waitpid(pid, NULL, 0);
		if (alarm(0))
			syslog(LOG_INFO, "user script \"%s\" finished", script);
		else
			syslog(LOG_INFO, "user script \"%s\" not finished, continuing anyway", script);
		return;
	}
	return;
}

void logger(char *cmd) {
	FILE *f = popen(cmd, "r");
	char buf[BUFSZ];
	while (fgets(buf, BUFSZ, f) != NULL) {
		*strchr(buf, '\n') = ' ';
		syslog(LOG_INFO, buf);
	}
	pclose(f);
}

void check_other_daemon() {
	char *pidf = "/var/run/sysctrl.pid";
	int fd = open(pidf, O_RDWR | O_CREAT | O_EXCL, S_IRUSR | S_IWUSR | S_IROTH);
	if (fd == -1 && errno == EEXIST) {
		FILE *fp = fopen(pidf, "r");
		pid_t opid;
		if (fscanf(fp, "%d", &opid) != 1) {
			syslog(LOG_ERR, "file %s exists but can't be read: %m", pidf);
			exit(1);
		}
		if (kill(opid, 0) == 0) {
			syslog(LOG_ERR, "Another instance with pid=%d, exists, exiting.", opid);
			exit(1);
		}
		fclose(fp);
		unlink(pidf);
		fd = open(pidf, O_RDWR | O_CREAT | O_EXCL, S_IRUSR | S_IWUSR | S_IROTH);
	}

	FILE *fp = fdopen(fd, "r+");
	fprintf(fp, "%d\n", getpid());
	fclose(fp);
}

/* rev-B1
for i in $(seq 5 5 180); do
	echo $i > /sys/class/hwmon/hwmon0/device/pwm1
	sleep 10
	echo -n "pwd=$i fan="
	cat /sys/class/hwmon/hwmon0/device/fan1_input
done

// pwd=5 fan=1958
pwd=10 fan=1998
pwd=15 fan=2056
pwd=20 fan=2082
pwd=25 fan=2137
pwd=30 fan=2184
pwd=35 fan=2224
pwd=40 fan=2286
pwd=45 fan=2329
pwd=50 fan=2397
pwd=55 fan=2457
pwd=60 fan=2495
pwd=65 fan=2600
pwd=70 fan=2642
pwd=75 fan=2715
pwd=80 fan=2792
pwd=85 fan=2891
pwd=90 fan=2978
pwd=95 fan=3052
pwd=100 fan=3171
pwd=105 fan=3255
pwd=110 fan=3366
pwd=115 fan=3485
pwd=120 fan=3614
pwd=125 fan=3780
pwd=130 fan=3932
pwd=135 fan=4096
pwd=140 fan=4237
pwd=145 fan=4551
pwd=150 fan=4593
pwd=155 fan=4915
pwd=160 fan=5228
pwd=165 fan=5585
pwd=170 fan=5851
pwd=175 fan=5649
pwd=180 fan=6467

 * fan = 0.00111642 * x^3 - 0.148356 * x^2 + 16.3374 * x + 1839.55
 * x = pwm (5..180)
 *
 * pwm = 2.66029e-9 * x^3 - 4.28952e-5 * x^2 + 0.244737 * x - 328.233
 * x = fan (1900...6500)
 */

float p2f[] = { 0.00111642, -0.148356, 16.3374, 1839.55 };
float f2p[] = { 2.66029E-9, -4.28952E-5, 0.244737, -328.233 };

float poly(float pwm, float coef[]) {
	int i;
	float ret = coef[0];
	for (i = 1; i < 4; i++)
		ret = pwm * ret + coef[i];
	return ret;
}

int syserrorlog(char *emsg) {
	int fd;
	char buf[BUFSZ] = "<li>";

	syslog(LOG_CRIT, emsg);
	
	if ((fd = open(syserrorfn, O_CREAT | O_WRONLY | O_APPEND, 0644 )) == -1) {
		syslog(LOG_ERR, "open %s: %m", syserrorfn);
		return -1;
	}
	strcat(buf, emsg);
	strcat(buf, "</li>\n");
	write(fd, buf, strlen(buf));
	close(fd);
	return 0;
}

/* log fan speed and system temperature to a file, to not flood syslog and loose important logs
 * When the 32KB file maximum size is reached, logging continues at the file beginning.
 * an "OLD:" line marks the beginning of old log entries
 */
void fanlog(float temp, int pwm, int fan) {
	static int fd = -1;
	int nc;
	char outstr[128], buf[128];
	time_t t;
	struct tm *tmp;

	if (fd == -1) {
		if ((fd = open(fantemplog, O_WRONLY | O_CREAT, 0644)) == -1) {
			syslog(LOG_ERR, "Can't open %s: %m", fantemplog);
			return;
		}
		lseek(fd, 0, SEEK_END);
	}
	if (lseek(fd, 0, SEEK_CUR) > 32768)
		lseek(fd, 0, SEEK_SET);
	else
		lseek(fd, -5, SEEK_CUR);

	t = time(NULL);
	tmp = localtime(&t);
	strftime(outstr, sizeof(outstr), "%b %d %T", tmp);
	nc = sprintf(buf, "%s\ttemp=%.1f\tpwm=%d\tfan=%d\nOLD:\n", outstr, temp, pwm, fan);
	write(fd, buf, nc);
}

enum ledmode {NA=-1, LEDOFF, LEDON, LEDBLINK};
enum ledprior {PHIGH=0, PMED, PLOW};
int leds_pqueue[] = {LEDOFF, LEDOFF, LEDOFF};

void leds_set(int priority, int mode) {
	//syslog(LOG_INFO, "pri=%d md=%d", priority, mode);
	leds_pqueue[priority] = mode;
}

/* this is a small improvement over leds handling, but not definitive!
 * this only maintains a "priority queue" for all leds altogether, but each led should be handleded
 * separately, together with its current state: trigger, brightness, delay_off, delay_on....
 * When a new led is set in the queue, the led current state should be saved in a stack; when the
 * led action is turned off, the state staved in the stack would be restored.
 * But it is too much work: having a priority queue for each led, where each priority level has its own stack!
 */
void leds_proc() {
	int i;
	for (i=PHIGH; i<=PLOW; i++) {
		switch (leds_pqueue[i]) {
			case NA: break;
			case LEDOFF: leds_off(); leds_pqueue[i] = NA; break;
			case LEDON: leds_on(); break;
			case LEDBLINK: leds_blink(); break;
		}
	}
}

int check_syserrlog() {
	struct stat buf;
	static int leds_state = 0;
	
	if (stat(syserrorfn, &buf)) {
		if (leds_state == 1) {
			// syslog(LOG_INFO, "Non existing \"%s\"", syserrorfn);
			leds_state = 0;
			leds_set(PLOW, LEDOFF); // leds_off();
		}
		return 0;
	}

	if (buf.st_size != 0) {
		if (leds_state == 0) {
			// syslog(LOG_INFO, "Non empty \"%s\"", syserrorfn);
			leds_state = 1;
			leds_set(PLOW, LEDON); //leds_on();
		}
		return 1;
	} else {
		if (leds_state == 1) {
			// syslog(LOG_INFO, "Empty \"%s\"", syserrorfn);
			leds_state = 0;
			leds_set(PLOW, LEDOFF); //leds_off();
		}
		return 0;
	}
}

int read_str_from_file(const char *filename, char *str, int sz) {
	int fd;
	int len;
	
	fd = open(filename, O_RDONLY);
	if (fd == -1) {
		syslog(LOG_ERR, "open %s: %m", filename);
		return -1;
	}
	len = read(fd, str, sz);
	close(fd);
	
	if (len < 1)
		return -1;
	str[len-1] = 0;
	return 0;
}

int write_str_to_file(const char *filename, char *str) {
	int fd, len;
	char buf[64];
	
	if ((fd = open(filename, O_WRONLY | O_TRUNC)) == -1) {
		if ((fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644)) == -1) {
			syslog(LOG_ERR, "open %s: %m", filename);
			return -1;
		}
	}
	strcpy(buf, str);
	len = strlen(buf);
	buf[len]='\n';
	write(fd, buf, len+1);
	close(fd);
	return 0;
}

int read_int_from_file(const char *filename, int *u) {
	char buf[64];
	if (read_str_from_file(filename, buf, 64))
		return -1;
	sscanf(buf, "%d", u);
	return 0;
}

int write_int_to_file(const char *filename, int u) {
	char buf[64];
	sprintf(buf, "%d", u);
	return write_str_to_file(filename, buf);
}

void check_board() {
	char res[64];

	if (read_str_from_file("/tmp/board", res, 64)) {
		syserrorlog("Can't read /tmp/board, exiting");
		exit(1);
	}
	if (strcmp("DNS-323-A1", res) == 0) {
		board = DNS_323_A1;
		leds[usb_led] = NULL; // box has no USB led
	} else if (strcmp("DNS-323-B1", res) == 0) {
		board = DNS_323_B1;
		leds[usb_led] = NULL;
	} else if (strcmp("DNS-323-C1", res) == 0) {
		board = DNS_323_C1;
		leds[usb_led] = NULL;
		args.lo_temp = 45;	// redefine defaults for C1. At temp > lo_temp, fan goes fast 
	}
	else if (strcmp("DNS-321-Ax", res) == 0) {
		board = DNS_321_Ax;
		leds[usb_led] = NULL;
		nslots = 2; // box has no USB plug
		args.lo_temp = 45;	// redefine defaults for D1. At temp > lo_temp, fan goes fast 
	}
	else if (strcmp("DNS-325-Ax", res) == 0) {
		board = DNS_325_Ax;
		args.lo_temp = 45;	// redefine defaults for D1. At temp > lo_temp, fan goes fast 
	}
	else if (strcmp("DNS-320-Ax", res) == 0) {
		board = DNS_320_Ax;
		args.lo_temp = 45;	// redefine defaults for D1. At temp > lo_temp, fan goes fast 
	}
	else if (strcmp("DNS-320L-Ax", res) == 0) {
		board = DNS_320L_Ax;
		args.lo_temp = 45;	// redefine defaults for D1. At temp > lo_temp, fan goes fast 
	}
	else if (strcmp("DNS-320-Bx", res) == 0) {
		board = DNS_320_Bx;
		args.lo_temp = 45;	// redefine defaults for D1. At temp > lo_temp, fan goes fast 
	}
	else if (strcmp("DNS-327L-Ax", res) == 0) {
		board = DNS_327L_Ax;
		leds[usb_led] = NULL; // box has no orange USB led
		args.lo_temp = 45;	// redefine defaults for D1. At temp > lo_temp, fan goes fast 
	}
	else {
		char buf[BUFSZ];
		snprintf(buf, BUFSZ, "Hardware board %s not supported, exiting.", res);
		syserrorlog(buf);
		exit(1);
	}
}

int read_fan(void) {
	int u = 0;
	read_int_from_file(sys_fan_input, &u);
	return u;
}

void write_pwm(int u) {
	static int old = -1;
	if (u != old) {
		old = u;
		write_int_to_file(sys_pwm, u);
	}
}

int read_pwm(void) {
	int u = 0;
	read_int_from_file(sys_pwm, &u);
	return u;
}

/* -for the DNS-320, a sh script is asynchronously writing the temperature to a file.
 * -for the DNS320L/DNS327L, the dns320l-daemon is asynchronously writing the temperature 
 * and fanspeed and reading desired fanspeed to a file, but using read() and write()
 * which are atomic and dont need a lock.
 */
#define LOCK_DIR "/var/lock/temp-lock"

void clearlock() {
	if (unlink(LOCK_DIR"/pid"))
		syslog(LOG_ERR, "unlink: %m");
	if (rmdir(LOCK_DIR))
		syslog(LOG_ERR, "rmdir: %m");
}

int dolock() {
	int i = 100;
	while(mkdir(LOCK_DIR, S_IRWXU)) {
		if(i-- == 0) {
			int u = 0;
			if (read_int_from_file(LOCK_DIR"/pid", &u)) {
				 /* assume stale, reuse lock and continue */
				syslog(LOG_INFO, "couldn't read "LOCK_DIR" pid owner.");
			} else {
				if (getpid() == u) {
					/* how?! assume OK, reuse lock and continue */
					syslog(LOG_INFO, "owner of "LOCK_DIR" exists, it's me!"); 
				} else {
					if (kill(u, 0)) {
						 /* reuse lock and continue */
						syslog(LOG_INFO, "owner of "LOCK_DIR" disappeared, removing stale lock.");
					} else {
						syserrorlog("owner of "LOCK_DIR" is alive, can't get lock, exiting.");
						exit(1);
					}
				}
			}
			break;
		}
		usleep(100000);
	}
	char buf[64];
	sprintf(buf, "%d\n", getpid()); /* write_int_to_file() don't write \n at end*/
	int fd = creat(LOCK_DIR"/pid", S_IRWXU);
	write(fd, buf, strlen(buf));
	close(fd);
	return 0;
}

int read_temp(void) {
	int u = 0;
	dolock();
	read_int_from_file(sys_temp_input, &u);
	clearlock();
	return u;
}

void fanctl(void) {
	static float temp = 0., log_temp = 0.;
	static int warn = 0, crit = 0, log_fan = 0;
	int fan, pwm;

	if (temp == 0.) { // zero has an exact float representation
		temp = read_temp() / 1000.;
		pwm = 0;
	} else {
		temp = 0.9 * read_temp() / 1000. + 0.1 * temp;
		pwm = read_pwm();
	}
	
	fan = read_fan();
	

	if ( (fabsf(temp - log_temp) > 1.0) || (abs(fan - log_fan) > 400)) {
		log_temp = temp;
		log_fan = fan;
		//syslog(LOG_INFO, "temp=%.1f	pwm=%d fan=%d", temp, pwm, fan);
		// temp/fan logs flood syslog for the 320L/327, use a file for logging
		fanlog(temp, pwm, fan);
	}

	if (board == DNS_323_A1 || board == DNS_323_B1) {
		float m = (args.hi_fan - args.lo_fan) * 1. / (args.hi_temp - args.lo_temp);
		float b = args.lo_fan - m * args.lo_temp;
		
		if (temp < (args.fan_off_temp - args.hist_temp))
			pwm = 0;
		else if (temp > (args.fan_off_temp + args.hist_temp))
			pwm = (int)poly(temp * m + b, f2p);
		
		if (fan >= args.max_fan_speed) {
			int tpwm = poly(args.max_fan_speed, f2p);
			if ( tpwm < pwm)
				pwm = tpwm;
		}
	} else { // Augusto Bott code
		switch (args.fan_mode) {
			case FAN_ALWAYS_OFF: pwm = PWM_OFF; break;
			case FAN_ALWAYS_SLOW: pwm = PWM_LOW; break;
			case FAN_ALWAYS_FAST: pwm = PWM_FAST; break;
			case FAN_AUTO:
				switch (fan) {
					case RPM_OFF:
						pwm = PWM_OFF;
						if (temp > (args.fan_off_temp + args.hist_temp))
							pwm = PWM_LOW;
						break;
					case RPM_LOW:
						pwm = PWM_LOW;
						if (temp < (args.fan_off_temp - args.hist_temp))
							pwm = PWM_OFF;
						else if (temp > (args.lo_temp + args.hist_temp))
							pwm = PWM_FAST;
						break;
					case RPM_FAST:
						pwm = PWM_FAST;
						if (temp < (args.lo_temp - args.hist_temp))
							pwm = PWM_LOW;
						break;
					default: // failsafe
						pwm = PWM_LOW;
				}
				break;
		}
	}
	write_pwm(pwm);

	if (temp > args.warn_temp && temp < args.crit_temp && warn == 0) {
		char buf[BUFSZ];
		snprintf(buf, BUFSZ, "WARNING TEMP: fan=%d temp=%.1f exceeded warn=%d",
			fan, temp, args.warn_temp);
		syserrorlog(buf);
		if (args.mail)
			smail(WARNT, fan, temp, args.warn_temp);
		exec_userscript(args.warn_temp_command, 20, NULL);
		warn = 1;
	}
	
	if (temp < args.warn_temp && warn == 1)
		warn = 0;
	
	if (temp > args.crit_temp && crit == 0) {
		char buf[BUFSZ];
		if (args.mail)
			smail(CRITT, fan, temp, args.crit_temp);
		snprintf(buf, BUFSZ, "OVERHEAT: fan=%d temp=%.1f exceeded critical=%d",
				 fan, temp, args.crit_temp);
		exec_userscript(args.crit_temp_command, 20, NULL);
		crit = 1;
	}

	if (temp < args.crit_temp && crit == 1)
		crit = 0;
}

#define WIN_CHECKPOWERMODE1 0xE5
#define WIN_CHECKPOWERMODE2 0x98

/* Check if the disk is in powersave-mode
 * Most code stolen from hdparm.
 * 1 = active, 0 = standby/sleep, -1 = unknown
 */
int check_powermode(char *dev) {
	char dsk[32] = "/dev/";
	strcat(dsk, dev);
	int fd;
	if ((fd = open(dsk, O_RDONLY)) == -1)
		return -1;

	unsigned char args[4] = { WIN_CHECKPOWERMODE1, 0, 0, 0 };
	int state;

	if (ioctl(fd, HDIO_DRIVE_CMD, &args)
	    && (args[0] = WIN_CHECKPOWERMODE2)	/* try again with 0x98 */
	    &&ioctl(fd, HDIO_DRIVE_CMD, &args)) {
		if (errno != EIO || args[0] != 0 || args[1] != 0) {
			state = -1;	/* "unknown"; */
		} else
			state = 0;	/* "sleeping"; */
	} else {
		state = (args[2] == 255) ? 1 : 0;
	}
	close(fd);
	return state;
}

/* number of disk read plus writes (is disk idle since last check?) */
unsigned long dstat(char *dsk) {
	char buf[128], fname[32] = "/sys/block/";
	unsigned long rd, wr;
	
	sprintf(fname, "/sys/block/%s/stat", dsk);
	
	if (read_str_from_file(fname, buf, 128))
		return 0;
	
	if (sscanf(buf, "%lu %*d %*d %*d %lu", &rd, &wr) != 2)
		return 0;
	//syslog(LOG_INFO, "%s: %lu %lu", dsk, rd, wr);
	return rd + wr;
}

/* spin-down a disk, to be used with USB drives where hdparm does not works.
 * stolen from hd-idle, https://sourceforge.net/projects/hd-idle/
 */
#include <scsi/sg.h>
#include <scsi/scsi.h>

void spindown_disk(const char *name) {
  struct sg_io_hdr io_hdr;
  unsigned char sense_buf[255];
  char dev_name[100];
  int fd;

  syslog(LOG_INFO, "force %s spindown\n", name);

  /* fabricate SCSI IO request */
  memset(&io_hdr, 0x00, sizeof(io_hdr));
  io_hdr.interface_id = 'S';
  io_hdr.dxfer_direction = SG_DXFER_NONE;

  /* SCSI stop unit command */
  io_hdr.cmdp = (unsigned char *) "\x1b\x00\x00\x00\x00\x00";

  io_hdr.cmd_len = 6;
  io_hdr.sbp = sense_buf;
  io_hdr.mx_sb_len = (unsigned char) sizeof(sense_buf);

  /* open disk device (kernel 2.4 will probably need "sg" names here) */
  snprintf(dev_name, sizeof(dev_name), "/dev/%s", name);
  if ((fd = open(dev_name, O_RDONLY)) < 0) {
    syslog(LOG_INFO, "error opening %s", dev_name);
    return;
  }

  /* execute SCSI request */
  if (ioctl(fd, SG_IO, &io_hdr) < 0) {
    char buf[100];
    snprintf(buf, sizeof(buf), "ioctl on %s:", name);
    syslog(LOG_INFO, "%s", buf);

  } else if (io_hdr.masked_status != 0) {
    syslog(LOG_INFO, "SCSI command failed with status 0x%02x\n",
            io_hdr.masked_status);
    /* jc:
	if (io_hdr.masked_status == CHECK_CONDITION) {
	  phex(sense_buf, io_hdr.sb_len_wr, "sense buffer:\n");
    }
    */
  }
  close(fd);
}

// FIXME support more than one USB disk
// this is a mess, because bink_leds() and md_stat() and check_syserrlog() also manipulate leds:
// if noleds == 0, use leds
// if noleds == 1, don't use leds
void hdd_powercheck(int noleds) {

	int i, dpm, dpmf = 0;
	unsigned long dst;
	char *dev, pled[16];
	
	for (i = 0; i < nslots; i++) {
		if (disks[i].dev == NULL)
			continue;
		dev = disks[i].dev;
		dpm = check_powermode(dev);

		if (dpm == -1 && disks[i].spindow_time > 0) { /* unknown, might happens for USB disks */
			time_t ctime = time(NULL);
			dst = dstat(dev);
			if (dst > disks[i].rdwr_cnt) { /* disk has been used, is active */
				disks[i].rdwr_cnt = dst;
				disks[i].last_access = ctime;
				dpm = 1; // mark as active
			} else {
				dpm = disks[i].power_state; // previous state
				if (disks[i].power_state != 0 &&
					ctime - disks[i].last_access > disks[i].spindow_time) {
					/* not active and unused for longer then programmed spindown */
						spindown_disk(dev);
						dpm = 0; // mark as sleep
				}
			}
		}

		if (disks[i].power_state != dpm) { // changed state to
			char *slot = disks[i].slot;
			if (dpm == 0) { // standby/sleep
				syslog(LOG_INFO, "%s disk (%s) standby", slot, dev);
				if (noleds == 0)
					led_blink(i, "10", "2000");
			} else { // active
				syslog(LOG_INFO, "%s disk (%s) wakeup", slot, dev);
				if (noleds == 0) 
					led_set(i, "0");
			}
		}
		disks[i].power_state = dpm;
		dpmf += dpm;
	}
	
	if (led_get(power_led, pled) != -1) { // power led not in use by other script...
		if (strcmp(pled, "none") == 0) {
			if (dpmf || ndisks == 0) // at least one disk is active
				led_set(power_led, "1");
			else
				led_set(power_led, "0");
		}
	}
}

/* returns 0 if not degraded */
int md_stat() {
	struct stat st;
	char buf[64], msg[64];
	int dev, cdegraded, ret = 0;
	char state[16], level[16];
	static int last_degraded = 0, degraded[10];
		
	if (stat("/proc/mdstat", &st))
		return 0;

	for (dev = 0; dev < 9; dev++) {
		sprintf(buf, "/dev/md%d", dev);
		if (stat(buf, &st))
			continue;

		sprintf(buf, "/sys/block/md%d/md/array_state", dev);
		read_str_from_file(buf, state, 64);
		if (strcmp(state, "inactive") != 0) {
			sprintf(buf, "/sys/block/md%d/md/level", dev);
			read_str_from_file(buf, level, 64);

			if (strcmp(level, "raid1") == 0 || strcmp(level, "raid5") == 0) {
				sprintf(buf, "/sys/block/md%d/md/degraded", dev);
				if (stat(buf, &st))
					continue;
				
				read_int_from_file(buf, &cdegraded);
				if (cdegraded == 0) 
					degraded[dev] = 0;
				else if (degraded[dev] == 0) {
						degraded[dev] = 1;
						last_degraded = 1;
						leds_set(PHIGH, LEDON); //leds_on();
						sprintf(msg, "Your md%d %s device is degraded!", dev, level);
						syserrorlog(msg);
					}
			} else
			degraded[dev] = 0;
		} else
			degraded[dev] = 0;
	}
	
	for (dev=0; dev<9; dev++)
		ret += degraded[dev];
		
	if (last_degraded == 1 && ret == 0) {
		last_degraded = 0;
		leds_set(PHIGH, LEDOFF); //leds_off();
	}
	return ret;
}

#define GPIO_INPUT_DEVICE "/dev/event0"

#define FRONT_EV	0x0074	// DNS-320/320L/323/325/327L front button event (KEY_POWER)
#define RESET_EV	0x0198	// DNS-320/320L/323/325/327L reset button event (KEY_RESTART)
#define USB_EV		0x0085	// DNS-320/320L/325/327L USB button event (KEY_COPY)

#define PRESSED		7		// bit 7 - pressed: 1, released 0


int button() {
	static int fd = -1; /* file needs to be keept open, otherwise events might be lost between invocations */
	struct input_event ev;
	int n, but = NO_BT;

	if (fd == -1) {
		fd = open(GPIO_INPUT_DEVICE, O_RDONLY | O_NONBLOCK);
		if (fd == -1) {
			syslog(LOG_ERR, "open %s: %m", GPIO_INPUT_DEVICE);
			return -1;
		}
	}

	n = read(fd, &ev, sizeof(struct input_event));
	
	if (n == sizeof(struct input_event) && ev.type == EV_KEY) {
		if (ev.code == FRONT_EV)
			but = FRONT_BT | (ev.value << PRESSED);
		else if (ev.code == RESET_EV)
			but = RESET_BT | (ev.value << PRESSED);
		else if (ev.code == USB_EV)
			but = USB_BT | (ev.value << PRESSED);

		do {
			usleep(10);
		} while ((n = read(fd, &ev, sizeof(struct input_event))) == 0);
		if (n != sizeof(struct input_event))
			syslog(LOG_ERR, "can't read EV_SYN key event");
		
	} else if (n < 0 && errno != EAGAIN) {
		syslog(LOG_ERR, "read from %s: %m", GPIO_INPUT_DEVICE);
		but = -1;
	}
	return but;
}

int debounce() {
	static int bt = NO_BT;
	int count, tbt;
	
	if (board == DNS_320L_Ax || board == DNS_320_Bx || board == DNS_327L_Ax) {
		int but;
		if (read_int_from_file(sys_power_button, & but) == 0 && but == 0) {
			syslog(LOG_INFO, "DNS320L/DNS327L power button pressed, poweroff.");
			poweroff();
		}
	}
		
	tbt = button();
	if (tbt == -1 || tbt == 0)	// no new event, return last button
		return bt;
	bt = tbt;	// events don't repeat, store this one

	// after 50 msec of no changes (end of bounce) return the last key pressed or released
	count = 50;
	while (count--) {
		if ((tbt = button()) != 0) { // new bounce event, re-arm iddle period 
			bt = tbt;
			count = 50;
		}
		usleep(1000);
	}
	if (bt & (1 << PRESSED))
		bt &= ~(1 << PRESSED);
	else
		bt = NO_BT;
	return bt;
}

void syswrite(char *fname, char *value) {
	write_str_to_file(fname, value);
}

void led_set(int which, char *mode) {
	char buf[128];
	
	if (leds[which] == NULL)
		return;

	sprintf(buf, "%s%s", leds[which], "trigger");
	syswrite(buf, "none");
	sprintf(buf, "%s%s", leds[which], "brightness");
	syswrite(buf, mode);
}

int led_get(int which, char *mode) {
	char buf1[128], buf2[128], *ts, *te;
	int u;
	
	if (leds[which] == NULL)
		return -1;
	
	sprintf(buf1, "%s%s", leds[which], "trigger");	
	if (read_str_from_file(buf1, buf2, 128))
		return -1;
	
	ts = strchr(buf2,'[');
	te = strchr(buf2,']');
	
	if (ts != NULL && te != NULL) {
		*te = '\0';
		strcpy(mode, ts + 1);
	} else if (ts == NULL && te == NULL)
		strcpy(mode, buf2);;
	
	sprintf(buf1, "%s%s", leds[which], "brightness");
	if (read_int_from_file(buf1, &u))
		return -1;
	return u;
}

void led_blink(int which, char *on, char *off) {
	char buf[128];
	
	if (leds[which] == NULL)
		return;

	led_set(which, "0");
	sprintf(buf, "%s%s", leds[which], "trigger");
	syswrite(buf, "timer");
	sprintf(buf, "%s%s", leds[which], "delay_on");
	syswrite(buf, on);
	sprintf(buf, "%s%s", leds[which], "delay_off");
	syswrite(buf, off);
}

void leds_on() {
	int i;
	for (i = 0; i < 2; i++)
		led_set(i, "1");
}

void leds_off() {
	int i;
	for (i = 0; i < 2; i++)
		led_set(i, "0");
}

void leds_blink() {
	int i;
	for (i = 0; i < 2; i++)
		led_blink(i, "250", "250");
}

void config(char *n, char *v) {
	if (strcmp(n, "lo_fan") == 0) {
		args.lo_fan = atoi(v);
	} else if (strcmp(n, "hi_fan") == 0) {
		args.hi_fan = atoi(v);
	} else if (strcmp(n, "lo_temp") == 0) {
		args.lo_temp = atoi(v);
	} else if (strcmp(n, "hi_temp") == 0) {
		args.hi_temp = atoi(v);
	} else if (strcmp(n, "hist_temp") == 0) {
		args.hist_temp = atof(v);
	} else if (strcmp(n, "fan_mode") == 0) {
		args.fan_mode = atoi(v);
		switch (args.fan_mode) {
			case FAN_ALWAYS_OFF: break;
			case FAN_ALWAYS_SLOW: break;
			case FAN_ALWAYS_FAST: break;
			case FAN_AUTO: break;
			default: args.fan_mode = FAN_AUTO; break;
		}
	} else if (strcmp(n, "fan_off_temp") == 0) {
		args.fan_off_temp = atoi(v);
	} else if (strcmp(n, "max_fan_speed") == 0) {
		args.max_fan_speed = atoi(v);
	} else if (strcmp(n, "crit_temp") == 0) {
		args.crit_temp = atoi(v);
	} else if (strcmp(n, "warn_temp") == 0) {
		args.warn_temp = atoi(v);
	} else if (strcmp(n, "mail") == 0) {
		args.mail = atoi(v);
	} else if (strcmp(n, "recovery") == 0) {
		args.recovery = atoi(v);			
	} else if (strcmp(n, "crit_temp_command") == 0) {
		args.crit_temp_command = checkfile(strdup(v));
	} else if (strcmp(n, "warn_temp_command") == 0) {
		args.warn_temp_command = checkfile(strdup(v));
	} else if (strcmp(n, "front_button_command1") == 0) {
		args.front_button_command1 = checkfile(strdup(v));
	} else if (strcmp(n, "front_button_command2") == 0) {
		args.front_button_command2 = checkfile(strdup(v));
	} else if (strcmp(n, "back_button_command") == 0) {
		args.back_button_command = checkfile(strdup(v));
	} else {
		syslog(LOG_ERR, "%s: Unknown option", n);
	}
}

void trim(char **str, char *end) {
	while (isspace(**str))
		++ * str;
	if (end)
		*end = 0;
	else
		end = *str + strlen(*str);
	while (end > *str && isspace(end[-1]))
		*--end = 0;

	/* remove quotes */
	if (**str == '"' && end[-1] == '"') {
		++*str;
		*--end = 0;
	}
}

void read_misc() {
	FILE *fp;
	int i, sl;
	char *cmd, *val, buf[BUFSZ];
	
	syslog(LOG_INFO, "reading /etc/misc.conf");
	fp = fopen("/etc/misc.conf", "r");
	if (fp == NULL) {
		syserrorlog("can't open /etc/misc.conf");
		return;
	}
	
	for (i = 0; i < nslots; i++)
		disks[i].spindow_time = 0;
	
	while (fgets(buf, BUFSZ, fp) != NULL) {
		cmd = strtok(buf, "=");
		val = strtok(NULL, "\n");               
        if (cmd == NULL || val == NULL || strlen(cmd) == 0 || strlen(val) == 0)
			continue;
		sscanf(val, "%d", &sl);
		if (strcmp(cmd, "HDSLEEP_LEFT") == 0) {
			disks[left_dev].spindow_time = sl*60;
		} else if (strcmp(cmd, "HDSLEEP_RIGHT") == 0) {
			disks[right_dev].spindow_time = sl*60;
		} else if (strcmp(cmd, "HDSLEEP_USB") == 0) {
			disks[usb_dev].spindow_time = sl*60;
		}
	}
	fclose(fp);
}

void read_bay() {
	FILE *fp;
	char *opt, *dev, buf[BUFSZ];
	int i;
	
	syslog(LOG_INFO, "reading /etc/bay");
	fp = fopen("/etc/bay", "r");
	if (fp == NULL) {
		syserrorlog("can't open /etc/bay");
		return;
	}
	
	for (i = 0; i < nslots; i++) {
		if (disks[i].dev)
			free(disks[i].dev);
		disks[i].dev = NULL;
	}

	ndisks = 0;
	while (fgets(buf, BUFSZ, fp) != NULL) {
		opt = strtok(buf, "=");
		dev = strtok(NULL, "\n");               
        if (opt == NULL || dev == NULL || strlen(opt) == 0 || strlen(dev) == 0)
			continue;
		if (strcmp(opt, "left_dev") == 0) {
			disks[left_dev].dev = strdup(dev);
			disks[left_dev].slot = "left";
			ndisks++;
		} else if (strcmp(opt, "right_dev") == 0) {
			disks[right_dev].dev = strdup(dev);
			disks[right_dev].slot = "right";
			ndisks++;
		} else if (strncmp(opt, "usb", 3) == 0 && strncmp(&opt[4], "_dev", 4) == 0) {
			disks[usb_dev].dev = strdup(dev);
			disks[usb_dev].slot = "usb";
			ndisks++;
		}
		
	}
	fclose(fp);	
}

void print_disks() {
	int i;
	syslog(LOG_INFO, "ndisks=%d", ndisks);
	for(i = 0; i < nslots; i++) {
		syslog(LOG_INFO, "%s %s rdwr=%lu last=%lu spindow=%lu power=%d\n",
			disks[i].dev, disks[i].slot, disks[i].rdwr_cnt,
			(unsigned long) disks[i].last_access, (unsigned long) disks[i].spindow_time,
			disks[i].power_state);
	}
}

void read_config() {
	FILE *fp;
	char str[128];
	int line = 0;
	char *n, *v, *ptr;
	syslog(LOG_INFO, "reading /etc/sysctrl.conf");
	fp = fopen("/etc/sysctrl.conf", "r");
	if (fp == NULL) {
		syslog(LOG_INFO, "No /etc/sysctrl.conf: %m\nUsing defaults");
		return;
	}

	while (fgets(str, sizeof(str), fp) != NULL) {
		line++;

		// strip comments
		if ((ptr = strchr(str, '#')) != NULL)
			*ptr = 0;

		// ignore empty lines
		if (strspn(str, " \f\n\r\t\v") == strlen(str))
			continue;

		// name = value
		n = str;
		v = strchr(str, '=');
		if (v == NULL)
			syserrorlog("Error in sysctrl.conf, '=' expected.");
		trim(&n, v++);
		trim(&v, NULL);
		config(n, v);
	}
	fclose(fp);
}

void print_config() {
	char *mode = "AUTO";
	syslog(LOG_INFO, "args.lo_fan=%d", args.lo_fan);
	syslog(LOG_INFO, "args.hi_fan=%d", args.hi_fan);
	syslog(LOG_INFO, "args.lo_temp=%d", args.lo_temp);
	syslog(LOG_INFO, "args.hi_temp=%d", args.hi_temp);
	syslog(LOG_INFO, "args.hist_temp=%.1f", args.hist_temp);
	switch(args.fan_mode) {
		case FAN_ALWAYS_OFF: mode="ALWAYS_OFF"; break;
		case FAN_ALWAYS_SLOW: mode="ALWAYS_SLOW"; break;
		case FAN_ALWAYS_FAST: mode="ALWAYS_FAST"; break;
		case FAN_AUTO: mode="AUTO"; break;
	}
	syslog(LOG_INFO, "args.fan_mode=%s", mode);
	syslog(LOG_INFO, "args.mail=%d", args.mail);
	usleep(1000); /* give syslog a break */
	syslog(LOG_INFO, "args.recovery=%d", args.recovery);
	syslog(LOG_INFO, "args.fan_off_temp=%d", args.fan_off_temp);
	syslog(LOG_INFO, "args.max_fan_speed=%d", args.max_fan_speed);
	syslog(LOG_INFO, "args.crit_temp=%d", args.crit_temp);
	syslog(LOG_INFO, "args.warn_temp=%d", args.warn_temp);
	usleep(1000); /* give syslog a break */
	syslog(LOG_INFO, "args.crit_temp_command=\"%s\"",
	       args.crit_temp_command);
	syslog(LOG_INFO, "args.warn_temp_command=\"%s\"",
	       args.warn_temp_command);
	syslog(LOG_INFO, "args.front_button_command1=\"%s\"",
	       args.front_button_command1);
	syslog(LOG_INFO, "args.front_button_command2=\"%s\"",
	       args.front_button_command2);
	syslog(LOG_INFO, "args.back_button_command=\"%s\"",
	       args.back_button_command);
}
