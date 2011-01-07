/* Copyright Joao Cardoso, 2009
 * Licence: GPLv2 
 *
 * Some code stolen from fonz fanctl and dns323-utils, 
 * other from Mark Lord <mlord@pobox.com> hdparm 
 *
 * To be used with Alt-F
 * 
 * -Provides fan control, hdd sleep detection, MD status,
 *  power and resete button handling:
 * -Reboots when power button pressed between 3 and 6 seconds (right led flashing)
 * -poweroff when power button pressed between 6 and 9 seconds (left led flashing)
 *  runs user suplied scripts on any of those events
 *  or when reset button momentary pressed (both left flashing)
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
#include <signal.h>
#include <sys/stat.h>
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
int md_stat();
int debounce();
int button(void);
void led(int which, char *value, char *mode, char *on, char *off);
void blink_leds(int leds);

void backup();
void reboot();
void poweroff();

int umountall();
int unswapall();
int killall();

void setup();
void mainloop();
void logger(char *cmd);
char *checkfile(char *fname);
void check_other_daemon();
void exec_userscript(char *script, int timeout, char *script_arg);
void read_config();
void print_config();

typedef struct {
	int lo_fan, hi_fan, lo_temp, hi_temp, mail, recovery, fan_off_temp,
		max_fan_speed, warn_temp, crit_temp;
	char *warn_temp_command, *crit_temp_command,
		*front_button_command1, *front_button_command2, *back_button_command;
} args_t;

// configuration default values, overriden by configuration files
args_t args =
    { 2000, 5000, 40, 50, 1, 1, 38, 5500, 52, 54, NULL, "/sbin/poweroff", NULL, NULL,
  NULL };

enum Boards { A1, B1, C1};
enum FanSpeed { FAN_OFF = 0, FAN_LOW =  127, FAN_FAST = 255 };
enum Leds { right_led = 1, left_led = 2 };
char *leds[] = { "", "/sys/class/leds/right:amber/",
	"/sys/class/leds/left:amber/"
};

char sys_pwm[64], sys_fan_input[64], sys_temp_input[64];

int board;

// hack! blink_leds() use it to signal() hdd_powercheck()
int leds_changed = 0;

#define NO_BT	0
#define FRONT_BT 1
#define BACK_BT	2

#define SCRIPT_TIMEOUT 5

#define IDLE	0
#define REBOOT	3
#define HALT	6
#define ABORT	9

#define BUFSZ 256

void alarm_handler()
{
}

int main(int argc, char *argv[])
{

	check_board();
	
	/* daemonize: fork, cd /, setsid, close io */
	daemon(0, 0);
	check_other_daemon();

	struct sigaction new;
	sigset_t smask;

	sigemptyset(&smask);
	new.sa_mask = smask;
	new.sa_flags = 0;

	//new.sa_handler = SIG_IGN;
	//sigaction(SIGTERM, &new, NULL);

	// timeout for user sripts
	new.sa_handler = alarm_handler;
	sigaction(SIGALRM, &new, NULL);

	// reread configureation file
	new.sa_handler = read_config;
	sigaction(SIGHUP, &new, NULL);

	/* log messages with syslog and write to /dev/console */
	openlog("sysctrl", LOG_CONS, LOG_DAEMON);
	syslog(LOG_INFO, "Starting");

	read_config();
	print_config();

	/* do the actual work */
	mainloop();

	return 0;
}

void mainloop()
{
	int bt, count = 0, state = IDLE;

	int powercheck_interval = 5;
	int powercheck_count = powercheck_interval - 1;

	int fan_interval = 30;
	int fan_count = fan_interval - 1;

	blink_leds(0);		// turn-off all leds

	// FIXME: MESS!!
	// the hdd standby leds interact with button leds. CHANGE program architecture

	while (1) {

		if ((++fan_count % fan_interval) == 0)
			fanctl();

		bt = debounce();
		count++;

		if ((++powercheck_count % powercheck_interval) == 0 && bt == NO_BT)
			hdd_powercheck(md_stat());

		if (bt && state == IDLE)
			blink_leds(0);

		if (bt == BACK_BT) {
			backup();
			continue;
		}

		switch (state) {
		case IDLE:
			if (bt == NO_BT) {
				count = 0;
			} else if (count == REBOOT) {
				state = REBOOT;
				// syslog(LOG_INFO, "iddle->reboot");
				blink_leds(right_led);
			}
			break;

		case REBOOT:
			if (bt == NO_BT) {
				state = IDLE;
				count = 0;
				blink_leds(0);
				reboot();
			} else if (count == HALT) {
				state = HALT;
				// syslog(LOG_INFO, "reboot->halt");
				blink_leds(left_led);
			}
			break;

		case HALT:
			if (bt == NO_BT) {
				state = IDLE;
				count = 0;
				blink_leds(0);
				poweroff();
			} else if (count == ABORT) {
				state = IDLE;
				// syslog(LOG_INFO, "halt->iddle");
				count = 0;
				blink_leds(0);
			}
			break;
		}

		sleep(1);
	}

	return;
}

// FIXME: misname
void backup()
{
	time_t count = time(NULL);
	syslog(LOG_INFO, "Entering Backup");

	blink_leds(right_led | left_led);
	
	while (debounce() == BACK_BT) {
		usleep(200000);
	}

	count = time(NULL) - count;

	if (args.recovery && count > 20) // twenty seconds
		exec_userscript("/usr/sbin/recover", 3, "f"); // clear flash, reboot
	else if (args.recovery && count > 10) 	// ten seconds
		exec_userscript("/usr/sbin/recover", 3, "t"); // telnet port 26
	else
		exec_userscript(args.back_button_command, 1, NULL);
	
	blink_leds(0);
}

void reboot()
{
	syslog(LOG_INFO, "Rebooting NOW");
	exec_userscript(args.front_button_command1, SCRIPT_TIMEOUT, NULL);
	execl("/bin/busybox", "reboot", NULL);
}

void poweroff()
{
	syslog(LOG_INFO, "Poweroff NOW");
	exec_userscript(args.front_button_command2, SCRIPT_TIMEOUT, NULL);
	execl("/bin/busybox", "poweroff", NULL);
}

char *checkfile(char *fname)
{
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
	if (pop_sys("grep '^from' /etc/msmtprc | cut -f2", to) == NULL) {
		syslog(LOG_ERR, "mail not configured");
		return;
	}
	
	FILE *fo = popen("/usr/bin/msmtp --read-recipients", "w");
	if (fo == NULL) {
		syslog(LOG_ERR, "error sending mail");
		return;
	}
	fprintf(fo, "To: %s"
		"Subject: Alt-F System Control %s message\n\n"
		"This is a %s message from %s\n"
		"Fan speed=%d\nSystem Temperature=%.1f\nLimit Temperature=%d\n\n"
		"This message will not be sent again unless the situation normalizes and reappears afterwards.", to, type, type, host, fan, temp, limit);
	fclose(fo);
}

void exec_userscript(char *script, int timeout, char *arg)
{
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
		if (waitpid(pid, NULL, 0) > 0)	// wait(NULL) not working!
			syslog(LOG_INFO, "user script \"%s\" finished", script);
		else
			syslog(LOG_ERR,
			       "user script \"%s\" did not finish in %d sec",
			       script, timeout);
		return;
	}			/* else
				   exit(1); // really?!   
				 */
	return;
}

void logger(char *cmd)
{
	FILE *f = popen(cmd, "r");
	char buf[BUFSZ];
	while (fgets(buf, BUFSZ, f) != NULL) {
		*strchr(buf, '\n') = ' ';
		syslog(LOG_INFO, buf);
	}
	pclose(f);
}

void check_other_daemon()
{
	char *pidf = "/var/run/sysctrl.pid";
	int fd =
	    open(pidf, O_RDWR | O_CREAT | O_EXCL, S_IRUSR | S_IWUSR | S_IROTH);
	if (fd == -1 && errno == EEXIST) {
		FILE *fp = fopen(pidf, "r");
		pid_t opid;
		if (fscanf(fp, "%d", &opid) != 1) {
			syslog(LOG_ERR, " file %s exists but can't be read: %m",
			       pidf);
			exit(1);
		}
		if (kill(opid, 0) == 0) {
			syslog(LOG_ERR, "Another instance with pid=%d, exists, exiting.",
			       opid);
			exit(1);
		}
		fclose(fp);
		unlink(pidf);
		fd = open(pidf, O_RDWR | O_CREAT | O_EXCL,
			  S_IRUSR | S_IWUSR | S_IROTH);
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

pwd=5 fan=1958
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

float poly(float pwm, float coef[])
{
	int i;
	float ret = coef[0];
	for (i = 1; i < 4; i++)
		ret = pwm * ret + coef[i];
	return ret;
}

int read_str_from_file(const char *filename, char *str, int sz)
{
	int fd;
	int len;

	fd = open(filename, O_RDONLY);
	if (fd == -1) {
		syslog(LOG_CRIT, "open %s: %m", filename);
		return -1;
	}
	len = read(fd, str, sz);
	close(fd);

	if (len < 1)
		return -1;
	str[len - 1] = 0;
	return 0;
}

int write_str_to_file(const char *filename, char *str)
{
	int fd;

	if ((fd = open(filename, O_WRONLY)) == -1) {
		fd = open(filename, O_WRONLY | O_CREAT, 0644);
		if (fd == -1) {
			syslog(LOG_CRIT, "open %s: %m", filename);
			return -1;
		}
	}
	write(fd, str, strlen(str));
	close(fd);
	return 0;
}

int read_int_from_file(const char *filename, int *u)
{
	char buf[64];
	if (read_str_from_file(filename, buf, 64))
		return -1;
	*u = atoi(buf);
	return 0;
}

int write_int_to_file(const char *filename, int u)
{
	int fd;
	char buf[64];

	fd = open(filename, O_WRONLY);
	if (fd == -1) {
		syslog(LOG_CRIT, "open %s: %m", filename);
		return -1;
	}
	sprintf(buf, "%d", u);
	write(fd, buf, strlen(buf));
	close(fd);
	return 0;
}

void check_board() {
	char res[64];
	if (read_str_from_file("/tmp/board", res, 64)) {
		syslog(LOG_CRIT, "sysctrl: Couldn't read /tmp/board, exiting");
		exit(1);
	}
	if (strncmp("A1", res, 2) == 0)
		board = A1;
	else if (strncmp("B1", res, 2) == 0)
		board = B1;
	else if (strncmp("C1", res, 2) == 0) {
		board = C1;
		args.lo_temp = 45;	// redefine defaults for C1. At temp > lo_temp, fan goes fast 
	}
	else {
		syslog(LOG_CRIT, "sysctrl: Hardware board %s not supported, exiting", res);
		exit(1);
	}
	
	// hope that enumeration don't change, else we have to read /sys/.../device/name
	int dev = 0;
	if (board == A1 || board == B1)
		dev = 1; 
		
	sprintf(sys_pwm, "/sys/class/hwmon/hwmon%d/device/pwm1", 1-dev);
	sprintf(sys_fan_input, "/sys/class/hwmon/hwmon%d/device/fan1_input", 1-dev);
	sprintf(sys_temp_input, "/sys/class/hwmon/hwmon%d/device/temp1_input", dev);
}

int read_fan(void)
{
	int u = 0;
	read_int_from_file(sys_fan_input, &u);
	return u;
}

void write_pwm(int u)
{
	write_int_to_file(sys_pwm, u);
}

int read_temp(void)
{
	int u = 0;
	read_int_from_file(sys_temp_input, &u);
	return u;
}

void fanctl(void)
{
	static float last_temp = 40.;
	static int warn = 0, crit = 0;
	int pwm;

	float m =
	    (args.hi_fan - args.lo_fan) * 1.0 / (args.hi_temp - args.lo_temp);
	float b = args.lo_fan - m * args.lo_temp;

	float temp = (read_temp() / 1000. + last_temp) / 2;
	int fan = read_fan();
	
	if (board != C1) {
		if (temp <= args.fan_off_temp)
			pwm = 0;
		else if (fan >= args.max_fan_speed)
			pwm = (int)poly(args.max_fan_speed, f2p);
		else
			pwm = (int)poly(temp * m + b, f2p);
	} else {
		if (temp <= args.fan_off_temp)
			pwm = FAN_OFF;
		else if (temp < args.lo_temp)
			pwm = FAN_LOW;
		else
			pwm = FAN_FAST;
	}
	
	write_pwm(pwm);

	if (fabsf(temp - last_temp) >= 0.2) {
		last_temp = temp;
		fan = read_fan();
		syslog(LOG_INFO, "temp=%.1f	 fan=%d", temp, fan);
	}

	if (temp >= args.warn_temp && temp < args.crit_temp && warn == 0) {
		syslog(LOG_CRIT,
			"WARNING TEMP: fan=%d temp=%.1f exceeded warn=%d",
			fan, temp, args.warn_temp);
		if (args.mail)
			smail(WARNT, fan, temp, args.warn_temp);
		exec_userscript(args.warn_temp_command, 20, NULL);
		warn = 1;
	}
	
	if (temp < args.warn_temp && warn == 1)
		warn = 0;
	
	if (temp >= args.crit_temp && crit == 0) {
		if (args.mail)
		smail(CRITT, fan, temp, args.crit_temp);
		syslog(LOG_CRIT,
		       "OVERHEAT: fan=%d temp=%.1f exceeded critical=%d",
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
int check_powermode(char *dev)
{
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

// THIS NEEDS A REWRITE! 
// use notify for /etc/bay and /etc/misc.conf changes,
// and read the configuration only on changes

// FIXME to support more than one USB disk (although none I have supports this)
// this is a mess, because bink_leds() and md_stat(), that also manipulate leds
// if noleds == 0, use leds and syslog
// if noleds == 1, don't use leds, logs to syslog
// if noleds == 2, don't use leds, don't log
void hdd_powercheck(int noleds)
{

	static int power_st[16] =
	    { -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, };
		
	static unsigned long old_rdwr[16];
	static int stmo[16];
	unsigned long rdwr;
	
	char buf[BUFSZ];

	char *dev, *bay;
	int st, idx, wled, refresh = 0;

	static time_t baytime;
	struct stat sb;
	FILE *fpb, *fpm;

	if (stat("/etc/bay", &sb)) {
		syslog(LOG_CRIT, "sysctrl: open /etc/bay: %m");
		return;
	}
	
	if (sb.st_mtime != baytime) {
		baytime = sb.st_mtime;
		led(left_led, "0", "none", NULL, NULL);
		led(right_led, "0", "none", NULL, NULL);
		refresh = 1;
	}

	fpb = fopen("/etc/bay", "r");
	if (fpb == NULL) {
		syslog(LOG_CRIT, "sysctrl: open /etc/bay: %m");
		return;
	}

	if (leds_changed) {
		leds_changed = 0;
		refresh = 1;
	}

	fpm = fopen("/etc/misc.conf", "r");
	if (fpm == NULL) {
			syslog(LOG_INFO, "sysctrl: open /etc/misc.conf: %m");
	}

	while (fgets(buf, BUFSZ, fpb) != NULL) {
		bay = strtok(buf, "=");
		dev = strtok(NULL, "\n");		
		if (bay == NULL || dev == NULL || strlen(bay) == 0
		    || strlen(dev) == 0)
			continue;
		
		char *p = strchr(bay,'_');
		if (p == NULL || (p != NULL && strcmp(p, "_dev") != 0))
			continue;

		idx = dev[2] - 'a';
		
		st = check_powermode(dev);
		
		if (fpm != NULL) {
			char ubay[16], cmd[32], ln[32];
			int n, tmo, i=0;
			
			while(bay[i] != '_')
				ubay[i] = toupper(bay[i++]);
			ubay[i]='\0';
			
			sprintf(cmd,"HDSLEEP_%s=%%d", ubay);			
			while (fgets(ln, BUFSZ, fpm) != NULL) {
				if ((n = sscanf(ln, cmd, &tmo)) == 1) {
					tmo = tmo * 60 / 5; // minutes to sec, sysctrl loop is 5 sec
					break;
				}
			}
			rewind(fpm);
						
			if (n == 1) {
				rdwr = dstat(dev);
				if (rdwr != old_rdwr[idx]) {
					old_rdwr[idx] = rdwr;
					stmo[idx] = 0;
				
				} else {
					stmo[idx]++;
					if (stmo[idx] > tmo && st == 1) {
						syslog(LOG_INFO, "Putting %s disk (%s) into sleep", bay, dev);
						sprintf(cmd, "/sbin/hdparm -y /dev/%s", dev);
						system(cmd);
					}
				}
			}
		}

		if (refresh || st != power_st[idx]) {
			power_st[idx] = st;
			if (strcmp(bay, "right_dev") == 0)
				wled = right_led;
			else if (strcmp(bay, "left_dev") == 0)
				wled = left_led;
			else
				wled = 0;

			if (st == 0) {	// standby
				switch (noleds) {
					case 0:
						led(wled, "1", "timer", "50", "2000");
						/* fall through */
					case 1:	
						syslog(LOG_INFO, "%s disk (%s) standby", bay, dev);
						break;
					case 2:
						break;
				}
			} else if (st == 1) {	// active
				switch (noleds) {
					case 0:
						led(wled, "0", "none", NULL, NULL);
						/* fall through */
					case 1:
						syslog(LOG_INFO, "%s disk (%s) wakeup", bay, dev);
						break;
					case 2:
						break;
				}
			}
		}
	}
	fclose(fpb);
	if (fpm != NULL)
		fclose(fpm);
}

/* returns 0 if not degraded nor rebuilding
 * returns 1 if degraded but not rebuilding
 * returns 2 if degraded and rebuilding
 */
int md_stat()
{
	struct stat st;
	char buf[64], msg[64];
	int dev, degraded, ret = 0;
	char state[16], level[16], action[16];
	static int recover = 0;

	if (stat("/proc/mdstat", &st))
		return 0;

	for (dev = 0; dev < 9; dev++) {
		sprintf(buf, "/dev/md%d", dev);
		if (stat(buf, &st))
			continue;

		sprintf(buf, "/sys/block/md%d/md/array_state", dev);
		read_str_from_file(buf, state, 64);
		sprintf(msg, "md%d: state=%s ", dev, state);

		if (strcmp(state, "inactive") != 0) {
			sprintf(buf, "/sys/block/md%d/md/level", dev);
			read_str_from_file(buf, level, 64);
			sprintf(msg + strlen(msg), "level=%s ", level);

			if (strcmp(level, "raid1") == 0 || strcmp(level, "raid5") == 0) {
				sprintf(buf, "/sys/block/md%d/md/degraded",
					dev);
				read_int_from_file(buf, &degraded);
				sprintf(msg + strlen(msg), "degraded=%d ",
					degraded);

				if (degraded != 0) {
					sprintf(buf,
						"/sys/block/md%d/md/sync_action",
						dev);
					read_str_from_file(buf, action, 64);
					sprintf(msg + strlen(msg), "action=%s",
						action);
					if (strcmp(action, "idle") == 0) {
						led(right_led, "1", "none",
						    NULL, NULL);
						led(left_led, "1", "none", NULL,
						    NULL);
						ret = 1;
					} else {
						blink_leds(right_led | left_led);
						ret = 2;
					}
					if (recover == 0)
						syslog(LOG_INFO, msg);
					recover = 1;
				}
			}
		}
	}
	if (ret == 0 && recover == 1) {
		recover = 0;
		blink_leds(0);
	}
	return ret;
}

/*
	front-button: should be debounced!

	sec=1246624645 usec=916710 type=1 code=74 value=1
	sec=1246624645 usec=916724 type=0 code=0 value=0
	sec=1246624645 usec=916752 type=1 code=74 value=0
	sec=1246624645 usec=916755 type=0 code=0 value=0
	sec=1246624645 usec=916805 type=1 code=74 value=1
	sec=1246624645 usec=916811 type=0 code=0 value=0
	sec=1246624648 usec=688130 type=1 code=74 value=0
	sec=1246624648 usec=688138 type=0 code=0 value=0

	back-button: no bounce

	sec=1246624676 usec=125396 type=1 code=198 value=1
	sec=1246624676 usec=125410 type=0 code=0 value=0
	sec=1246624678 usec=70803 type=1 code=198 value=0
	sec=1246624678 usec=70813 type=0 code=0 value=0

	type:
	1 EV_KEY
	0 EV_SYN

	code:
	74	FRONT_BUTTON[B
	198 BACK_BUTTON

	};
*/

#define GPIO_INPUT_DEVICE "/dev/event0"
#define FRONT_BUTTON	0x74	// front button event
#define BACK_BUTTON	0x198		// back button event

#define PRESSED 0x01	// bit 0 - pressed: 1, released 0
#define FRONT 0x02		// bit 1 - front button
#define BACK 0x04		// bit 2 - back button

int button()
{
	static int fd = 0;	// odd, if fd is not static read() *always* return EAGAIN
	struct input_event ev;
	int n, but = 0;

	if (fd == 0) {
		fd = open(GPIO_INPUT_DEVICE, O_RDONLY | O_NONBLOCK);
		if (fd == -1) {
			syslog(LOG_CRIT, "open %s: %m", GPIO_INPUT_DEVICE);
			fd = 0;
			return -1;
		}
	}

	n = read(fd, &ev, sizeof(struct input_event));
	
	if (n == sizeof(struct input_event) && ev.type == EV_KEY) {
		if (ev.code == FRONT_BUTTON)
			but = FRONT | ev.value;
		else if (ev.code == BACK_BUTTON)
			but = BACK | ev.value;

		// syslog(LOG_INFO, "sec=%d usec=%d type=%x code=%x value=%x\n",
		//	(int) ev.time.tv_sec, (int) ev.time.tv_usec, ev.type, ev.code, ev.value);

		// wait for EV_SYN, from 3 ro 17 usec
		do {
			usleep(10);
		} while ((n = read(fd, &ev, sizeof(struct input_event))) == 0);
		if (n != sizeof(struct input_event))
			syslog(LOG_CRIT, "couldn't read EV_SYN key event");
		
	} else if (n < 0 && errno != EAGAIN) {
		syslog(LOG_CRIT, "read from %s: %m", GPIO_INPUT_DEVICE);
		return -1;
	}

	return but;
}

int debounce()
{
	static int bt = NO_BT;
	int count, tbt;
	
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

	if (bt & PRESSED) {
		if (bt & FRONT)
			bt = FRONT_BT;
		else if (bt & BACK)
			bt = BACK_BT;
	} else
		bt = NO_BT;

	//syslog(LOG_INFO, "button %d ", bt);

	return bt;
}

void syswrite(char *fname, char *value)
{
	int fd;
	if ((fd = open(fname, O_WRONLY)) == -1) {
		syslog(LOG_INFO, "open %s: %m", fname);
		return;
	}
	write(fd, value, strlen(value));
	close(fd);
}

void led(int which, char *value, char *mode, char *on, char *off)
{
	char buf[128];

	if (which == 0 || which > 2 )
		return;

	sprintf(buf, "%s%s", leds[which], "brightness");
	syswrite(buf, value);

	sprintf(buf, "%s%s", leds[which], "trigger");
	syswrite(buf, mode);

	if (strcmp(mode, "timer") == 0) {

		sprintf(buf, "%s%s", leds[which], "delay_on");
		syswrite(buf, on);

		sprintf(buf, "%s%s", leds[which], "delay_off");
		syswrite(buf, off);
	}
}

/* arg: 'leds' is a bitmask */
void blink_leds(int leds)
{
	int i;
	for (i = 0; i < 3; i++) {
		if (leds & 1 << i)
			led(1 << i, "0", "timer", "250", "250"); // each blink is 0.5 sec, good for counting seconds in recover mode.
		else
			led(1 << i, "0", "none", NULL, NULL);
	}
	leds_changed = 1;
}

void config(char *n, char *v)
{
	if (strcmp(n, "lo_fan") == 0) {
		args.lo_fan = atoi(v);
	} else if (strcmp(n, "hi_fan") == 0) {
		args.hi_fan = atoi(v);
	} else if (strcmp(n, "lo_temp") == 0) {
		args.lo_temp = atoi(v);
	} else if (strcmp(n, "hi_temp") == 0) {
		args.hi_temp = atoi(v);
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
		syslog(LOG_CRIT, "%s: Unknown option, exiting", n);
		exit(1);
	}
}

void trim(char **str, char *end)
{
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

void read_config()
{
	FILE *fp;
	char str[128];
	int line = 0;
	char *n, *v, *ptr;
	syslog(LOG_INFO, "reading /etc/sysctrl.conf");
	fp = fopen("/etc/sysctrl.conf", "r");
	if (fp == NULL) {
		syslog(LOG_INFO,
		       "cant open /etc/sysctrl.conf: %m\nUsing defaults");
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
		if (v == NULL) {
			syslog(LOG_CRIT,
			       "Error in config, line %d. '=' expected.\nExiting",
			       line);
			exit(1);
		}
		trim(&n, v++);
		trim(&v, NULL);
		config(n, v);
	}
	fclose(fp);
}

void print_config()
{
	syslog(LOG_INFO, "args.lo_fan=%d", args.lo_fan);
	syslog(LOG_INFO, "args.hi_fan=%d", args.hi_fan);
	syslog(LOG_INFO, "args.lo_temp=%d", args.lo_temp);
	syslog(LOG_INFO, "args.hi_temp=%d", args.hi_temp);
	syslog(LOG_INFO, "args.mail=%d", args.mail);
	syslog(LOG_INFO, "args.recovery=%d", args.recovery);
	syslog(LOG_INFO, "args.fan_off_temp=%d", args.fan_off_temp);
	syslog(LOG_INFO, "args.max_fan_speed=%d", args.max_fan_speed);
	syslog(LOG_INFO, "args.crit_temp=%d", args.crit_temp);
	syslog(LOG_INFO, "args.warn_temp=%d", args.warn_temp);
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
