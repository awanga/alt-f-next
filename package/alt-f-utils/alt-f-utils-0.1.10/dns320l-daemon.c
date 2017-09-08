/*

  Simple system daemon for D-Link DNS-320L

  (c) 2013 Andreas Boehler, andreas _AT_ aboehler.at
  
  This code is based on a few other people's work and in parts shamelessly copied.
  The ThermalTable was provided by Lorenzo Martignoni and the fan control 
  algorithm is based on his fan-daemon.py implementation.
  
  The MCU protocol was reverse engineered by strace() calls to up_send_daemon and
  up_read_daemon of the original firmware.

  This program is free software: you can redistribute it and/or modify it under
  the terms of the GNU General Public License as published by the Free Software
  Foundation, either version 3 of the License, or (at your option) any later
  version.

  This program is distributed in the hope that it will be useful, but WITHOUT
  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
  FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
  details.

  You should have received a copy of the GNU General Public License along with
  this program. If not, see <http://www.gnu.org/licenses/>.
  
  Heavily modified and adapted to Alt-F by Joao Cardoso, joao fs cardoso gmail com

*/

#include <errno.h>
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <signal.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/time.h>
#include <time.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/un.h>
#include <sys/uio.h>
#include <syslog.h>
#include <ctype.h>

#include "dns320l.h"
#include "dns320l-daemon.h"

int ls; // socket descriptor
int fd; // serial descriptor 

// global to keep synchronized between user commands and mainloop

int fanSpeed = -1; 
char curr_led_trigger[32] = "";
int curr_led_brightness = -1;

char sys_pled_trigger[] = "/tmp/sys/power_led/trigger",
	sys_pled_brightness[] = "/tmp/sys/power_led/brightness",
	sys_pwm[] = "/tmp/sys/pwm1",
	sys_fan_input[] = "/tmp/sys/fan1_input",
	sys_temp_input[] = "/tmp/sys/temp1_input";

DaemonConfig stDaemonConfig;
  
/** @file dns320l-daemon.c
    @brief Implementation of a free system daemon replacement for
           the D-Link DNS-320L NAS
    @author Andreas Boehler, andreas _AT_ aboehler.at
    @version 1.0
    @date 2013/09/12
*/

void cleanup(int shut, int s, int howmany) {
	int retval;

	/*
	* Shutdown and close sock1 completely.
	*/
	if (shut) {
		retval = shutdown(s, howmany);
		if (retval == -1)
			syslog(LOG_ERR, "shutdown: %m");
	}
	
	retval = close (s);
	if (retval)
		syslog(LOG_ERR, "close: %m");
} 

static void quithandler(int sig) {
	if (stDaemonConfig.xcmd == 0) {
		syslog(LOG_INFO, "Quit Handler called");
		cleanup(0, ls, 1);
		unlink(stDaemonConfig.serverName);
	}
	exit(EXIT_SUCCESS);
}

static void debughandler(int sig) {
	syslog(LOG_INFO, "Setting loglevel to debug");
	setlogmask(LOG_UPTO(LOG_DEBUG));
}

static void infohandler(int sig) {
	syslog(LOG_INFO, "Setting loglevel to info");
	setlogmask(LOG_UPTO(LOG_INFO));
}
		
int set_interface_attribs (int fd, int speed, int parity) {
	struct termios tty;
	memset (&tty, 0, sizeof tty);
	if (tcgetattr (fd, &tty) != 0) {
		syslog(LOG_ERR, "error from tcgetattr: %m");
		return -1;
	}

	cfsetospeed (&tty, speed);
	cfsetispeed (&tty, speed);

	tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;     // 8-bit chars
	// disable IGNBRK for mismatched speed tests; otherwise receive break
	// as \000 chars
	tty.c_iflag &= ~IGNBRK;         // ignore break signal
	tty.c_lflag = 0;                // no signaling chars, no echo,
	// no canonical processing
	tty.c_oflag = 0;                // no remapping, no delays
	tty.c_cc[VMIN]  = 0;            // read doesn't block
	tty.c_cc[VTIME] = 5;            // 0.5 seconds read timeout

	tty.c_iflag &= ~(IXON | IXOFF | IXANY); // shut off xon/xoff ctrl

	tty.c_cflag |= (CLOCAL | CREAD);// ignore modem controls,
	// enable reading
	tty.c_cflag &= ~(PARENB | PARODD);      // shut off parity
	tty.c_cflag |= parity;
	tty.c_cflag &= ~CSTOPB;
	tty.c_cflag &= ~CRTSCTS;

	if (tcsetattr (fd, TCSANOW, &tty) != 0) {
		syslog(LOG_ERR, "error from tcsetattr: %m");
		return -1;
	}
	return 0;
}

void set_blocking (int fd, int should_block) {
	struct termios tty;
	memset (&tty, 0, sizeof tty);
	if (tcgetattr (fd, &tty) != 0) {
		syslog(LOG_ERR, "error from tggetattr: %m");
		return;
	}

	tty.c_cc[VMIN]  = should_block ? 1 : 0;
	tty.c_cc[VTIME] = 5;            // 0.5 seconds read timeout

	if (tcsetattr (fd, TCSANOW, &tty) != 0)
		syslog(LOG_ERR, "error setting term attributes: %m");
}

int CheckResponse(char *buf, char *cmd, int len) {
	int i;
	int failure = 0;

	// Attention, 5 is hardcoded here and never checked!
	for(i = 0; i < 5; i++) {
		if(buf[i] != cmd[i]) {
			syslog(LOG_ERR, "Char %i is %i but should be %i", i, buf[i], cmd[i]);
			failure = 1;
			break;
		}
	}
	
	if(failure) {
		for(i = 0; i < len; i++) {
			syslog(LOG_DEBUG, "Buf/Cmd %i: %i %i", i, buf[i], cmd[i]);
		}
		return ERR_WRONG_ANSWER;
	}
/*  if(buf[len-1] != cmd[len-1])
	{
		syslog(LOG_ERR, "Last character does not match! Char %i is %i but should be %i\n", len-1, buf[len-1], cmd[len-1]);
		return ERR_WRONG_ANSWER;
	}
*/
	return SUCCESS;
}

void ClearSerialPort(int fd) {
	char buf[100];
	struct pollfd fds[1];

	fds[0].fd = fd;
	fds[0].events = POLLIN;
	int n = 0;
	int pollrc;
	pollrc = poll(fds, 1, 0);
	if(pollrc > 0) {
		if(fds[0].revents & POLLIN) {
			syslog(LOG_DEBUG, "Clearing Serial Port...");
			do {
				n = read(fd, buf, sizeof(buf));
			} while(n == sizeof(buf));
		}
	}
}

int SendCommand(int fd, char *cmd, char *outArray) {
	int nRetries = -1;
	int ret;

	do {
		ret = _SendCommand(fd, cmd, outArray);
		nRetries++;
		if (ret != SUCCESS)
			syslog(LOG_DEBUG, "Try number: %i", nRetries+1);
	} while((ret != SUCCESS) && (nRetries < stDaemonConfig.nRetries));

	return ret;
}

int _SendCommand(int fd, char *cmd, char *outArray) {
	int n;
	int i;
	int j;
	ssize_t count;

	char buf[16]; // We need to keep the DateAndTime values here
	// Yes, we're sending byte by byte here - b/c the lenght of
	// commands and responses can vary!
	
	ClearSerialPort(fd); // We clear the serial port in case
	// some old data from a previous request is still pending

	i = 0;
	do {
		count = write(fd, &cmd[i], 1);
		i++;
		usleep(100); // The MCU seems to need some time..
		if(count != 1){
			syslog(LOG_ERR, "Error writing byte %i: %i, count: %i", (i-1), cmd[i-1], count);
			return ERR_WRITE_ERROR;
		}
	} while(cmd[i-1] != CMD_STOP_MAGIC);

	i = 0;
	do {
		n = read(fd, &buf[i], 1);
		i++;
	} while((n == 1) && (buf[i-1] != CMD_STOP_MAGIC) && i < sizeof(buf));

	if(buf[i-1] != CMD_STOP_MAGIC){
		syslog(LOG_ERR, "Got no stop magic, but read %i bytes!", i);
		for(j = 0; j < i; j++) {
			syslog(LOG_DEBUG, "Buf %i: %i", j, buf[j]);
		}
		return ERR_WRONG_ANSWER;
	} else {
		// If outArray is not NULL, an answer was requested
		if(outArray != NULL) {
			if(CheckResponse(buf, cmd, i) != SUCCESS) {
				return ERR_WRONG_ANSWER;
			}
			// Copy the answer to the outArray
			for(j = 0; j < i; j++) {
				outArray[j] = buf[j];
			}
			usleep(20000); // Give the µC some time to answer...

			// Wait for ACK from Serial
			i = 0;
			do {
				n = read(fd, &buf[i], 1);
				i++;
			} while((n == 1) && (buf[i-1] != CMD_STOP_MAGIC) && i < sizeof(buf));


			if(buf[i-1] != CMD_STOP_MAGIC) {
				syslog(LOG_ERR, "Got no stop magic!");
				for(j = 0; j < i; j++) {
					syslog(LOG_DEBUG, "Buf %i: %i", j, buf[j]);
				}

				return ERR_WRONG_ANSWER;
			}

			CheckResponse(buf, AckFromSerial, i);
			//syslog(LOG_DEBUG, "Returning %i read bytes", n);
			return SUCCESS;
		} else {
			// Only wait for ACK if no response is expected
			return CheckResponse(buf, AckFromSerial, i);
		}
	}
}

int simple_cmd(char *mcmd, char *retMessage, int bufSize) {
	if(SendCommand(fd, mcmd, NULL) == SUCCESS) {
		strncpy(retMessage, "OK", bufSize);
		return 0;
	}
	
	strncpy(retMessage, "ERR", bufSize);
	return 1;
}

int simple_cmd2(char *mcmd, char *retMessage, int bufSize) {
	char buf[16];
	int len;
	
	if(SendCommand(fd, mcmd, buf) > ERR_WRONG_ANSWER) {
		snprintf(retMessage, bufSize, "%d", buf[5]);
		len = strlen(retMessage);
		if(bufSize > 1)
			retMessage[len] = '\0';
		return 0;	
	}
	
	strncpy(retMessage, "ERR", bufSize);
	return 1;
}

int setfan_cmd(char *mcmd, char *retMessage, int bufSize) {
	char *buf = "0";
	
	if (simple_cmd(mcmd, retMessage, bufSize) == 0) {
		switch (mcmd[3]) {
			case 0:
				buf = "0";
				fanSpeed = 0;
				break;
			case 1:
				buf = "3000";
				fanSpeed = 1;
				break;
			case 2:
				buf = "6000";
				fanSpeed = 2;
				break;
		}
		write_str_to_file(sys_fan_input, buf);
		strncpy(retMessage, "OK", bufSize);
		syslog(LOG_DEBUG, "fan: %s", buf);
		return 0;
	}
	strncpy(retMessage, "ERR", bufSize);
	return 1;
}
	
int gettemperature_cmd(char *mcmd, char *retMessage, int bufSize) {
	char buf[16];
	int tmp;
	
	if(SendCommand(fd, mcmd, buf) > ERR_WRONG_ANSWER) {
      tmp = ThermalTable[(int)buf[5]];
      snprintf(retMessage, bufSize, "%d", tmp*1000);
      write_str_to_file(sys_temp_input, retMessage);
    } else {
      strncpy(retMessage, "ERR", bufSize);
      return 1;
    }
  return 0;
}

int setpowerled_cmd(char *mcmd, char *retMessage, int bufSize) {
	
	if (simple_cmd(mcmd, retMessage, bufSize) == 0) {
		switch (mcmd[3]) {
			case 0: // led off
				strcpy(curr_led_trigger, "none");
				curr_led_brightness = 0;
				break;
			case 1: // led on
				strcpy(curr_led_trigger, "none");
				curr_led_brightness = 1;
				break;
			case 2: // blink led
				strcpy(curr_led_trigger, "timer");
				break;
		}
		write_str_to_file(sys_pled_trigger, curr_led_trigger);
		write_int_to_file(sys_pled_brightness, curr_led_brightness);
		syslog(LOG_DEBUG, "led: %s %d", curr_led_trigger, curr_led_brightness);
		strncpy(retMessage, "OK", bufSize);
		return 0;
	}
	strncpy(retMessage, "ERR", bufSize);
	return 1;
}

int systohc_cmd(char *mcmd, char *retMessage, int bufSize) {
	 char cmdBuf[16];
	 time_t sysTime;
	 struct tm *strSetTime;
	 int i;
	
    for(i = 0; i < 13; i++)
      cmdBuf[i] = mcmd[i];
	
    sysTime = time(NULL);
    strSetTime = gmtime(&sysTime);
    // Put the current local time into the command buffer
    cmdBuf[5] = (char)strSetTime->tm_sec;
    cmdBuf[6] = (char)strSetTime->tm_min;
    cmdBuf[7] = (char)strSetTime->tm_hour;
    cmdBuf[8] = (char)strSetTime->tm_wday;
    cmdBuf[9] = (char)strSetTime->tm_mday;
    cmdBuf[10] = (char)(strSetTime->tm_mon + 1);
    cmdBuf[11] = (char)(strSetTime->tm_year - 100);

	// And modify the values so that the MCU understands them...
    for(i = 5; i < 12; i++)
      cmdBuf[i] = ((cmdBuf[i] / 10) << 4) + (cmdBuf[i] % 10);

    if(SendCommand(fd, cmdBuf, NULL) == SUCCESS)
      strncpy(retMessage, "OK", bufSize);
    else {
      strncpy(retMessage, "ERR", bufSize);
      return 1;
    }
    return 0;
}

int hctosys_cmd(char *mcmd, char *retMessage, int bufSize) {
	struct tm strTime;
	struct timeval setTime;
	time_t rtcTime;
	time_t sysTime;
	char timeStr[100];
	char buf[16];
	int i;
	char *tz;
	
    if(SendCommand(fd, RDateAndTimeCmd, buf) > ERR_WRONG_ANSWER) {
      for(i = 5; i < 12; i++)
        buf[i] = (buf[i] & 0x0f) + 10 * ((buf[i] & 0xf0) >> 4); // The other end is a µC (doh!)

      strTime.tm_year = (100 + (int)buf[11]);
      strTime.tm_mon = buf[10]-1;
      strTime.tm_mday = buf[9];
      strTime.tm_hour = buf[7];
      strTime.tm_min = buf[6];
      strTime.tm_sec = buf[5];
      strTime.tm_isdst = -1;

	// rtcTime = mktime(&strTime);
	tz = getenv("TZ");
	setenv("TZ", "", 1);
	tzset();
	rtcTime = mktime(&strTime);
	if (tz)
		setenv("TZ", tz, 1);
	else
		unsetenv("TZ");
	tzset();

      strcpy(timeStr, ctime(&rtcTime));
      // Retrieve system time
      sysTime = time(NULL);
      setTime.tv_sec = rtcTime;
      setTime.tv_usec = 0;
      // Set the time and print the difference on success
      if(settimeofday(&setTime, NULL) != 0)
        strncpy(retMessage, "ERR", bufSize);
      else
        snprintf(retMessage, bufSize, "%sSys: %sDiff: %.fs", timeStr, ctime(&sysTime), difftime(sysTime, rtcTime));
    } else {
      strncpy(retMessage, "ERR", bufSize);
      return 1;
    }
    return 0;
}

int readrtc_cmd(char *mcmd, char *retMessage, int bufSize) {
	struct tm strTime;
	time_t rtcTime;
	char timeStr[100];
	char buf[16];
	int i;
	
    if(SendCommand(fd, mcmd, buf) > ERR_WRONG_ANSWER) {
      for(i = 5; i < 12; i++)
        buf[i] = (buf[i] & 0x0f) + 10 * ((buf[i] & 0xf0) >> 4); // The other end is a µC (doh!)

      strTime.tm_year = (100 + (int)buf[11]);
      strTime.tm_mon = buf[10]-1;
      strTime.tm_mday = buf[9];
      strTime.tm_hour = buf[7];
      strTime.tm_min = buf[6];
      strTime.tm_sec = buf[5];
      strTime.tm_isdst = -1;   
      rtcTime = mktime(&strTime);
      strcpy(timeStr, ctime(&rtcTime));
	  timeStr[strlen(timeStr)-1] = '\0';
      snprintf(retMessage, bufSize, "%s", timeStr);
    } else {
      strncpy(retMessage, "ERR", bufSize);
      return 1;
    }
    return 0;
}

int shutdowndaemon_cmd(char *mcmd, char *retMessage, int bufSize) {
    strncpy(retMessage, "OK", bufSize);
    return 3;
}

int quit_cmd(char *mcmd, char *retMessage, int bufSize) {
    strncpy(retMessage, "Bye\n", bufSize);
    return 2;
  }
  
int help_cmd(char *mcmd, char *retMessage, int bufSize) {
	int i;
	
	strncpy(retMessage, "Available Commands:\n\n", bufSize);
	for (i = 0; i < sizeof(cmds)/sizeof(cmd_t); i++) {
		strncat(retMessage, cmds[i].ucmd, bufSize);
		strncat(retMessage, ", ", bufSize);
	}
	retMessage[strlen(retMessage)-2] = 0;
	strncat(retMessage, ".\n", bufSize);
	return 1;
}
	
int HandleCommand(char *message, int messageLen, char *retMessage, int bufSize) {
	int i;
	for (i = 0; i < sizeof(cmds)/sizeof(cmd_t); i++) {
		if (strcmp(cmds[i].ucmd, message) == 0) {
			syslog(LOG_INFO, "Handling Command: %s", message);
			if(cmds[i].func != NULL)
				return cmds[i].func(cmds[i].mcmd, retMessage, bufSize);
		}
	}
	sprintf(retMessage,"Unknown command \"%s\"", message);
	syslog(LOG_INFO, "Unknown Command: %s", message);
	return 1;
}

//jc: copied from sysctrl.c

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
		fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
		if (fd == -1) {
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

//jc: end-of copied from sysctrl.c

int demonize() {	
	/* dont fork, as it is to be respanwned by init and can't die */
	
	umask(0);
	
	if((chdir("/")) < 0) {
		syslog(LOG_ERR, "Could not chdir: %m");
		return EXIT_FAILURE;
	}
	
	close(STDIN_FILENO);
	close(STDOUT_FILENO);
	close(STDERR_FILENO);
	
	return 0;
}

int get_socket(struct sockaddr_un *server) {

	int lls, opt;
	
	if ((lls = socket (AF_UNIX, SOCK_STREAM, 0)) == -1) {
		syslog(LOG_ERR, "socket: %m");
		exit(EXIT_FAILURE);
	}
	
	if (setsockopt(lls, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof opt) < 0) {
		syslog(LOG_ERR, "setsockopt: %m");
		exit(EXIT_FAILURE);
	}
	
	server->sun_family = AF_UNIX;
	strcpy(server->sun_path, stDaemonConfig.serverName);
	
	return lls;
}

void set_serial() {
	fd = open (stDaemonConfig.portName, O_RDWR | O_NOCTTY | O_SYNC);
	if (fd < 0) {
		syslog(LOG_ERR, "error opening %s: %m", stDaemonConfig.portName);
		exit(EXIT_FAILURE);  
	}
	
	set_interface_attribs (fd, B115200, 0);  // set speed to 115,200 bps, 8n1 (no parity)
	set_blocking (fd, 0);                // set no blocking
}

int set_server() {
	return 0;
}

/* in xcmd mode, if another instance is already listening on socket
 * go to client mode and send the command to it;
 * If no other instance is listening send the command directly to the MCU
 */
int client_cmd(char *xcmd) {
	
	struct sockaddr_un server;
	int ls, st = 0;
	
	char msg[512];
	int n;
	
	ls = get_socket(&server);

	if (connect(ls, (struct sockaddr *) &server, sizeof(struct sockaddr_un)) == -1) {
		/* no running server, send command to MCU*/

		syslog(LOG_INFO, "No server, send cmd directly to MCU");
		set_serial();
		st = HandleCommand(xcmd, strlen(xcmd), msg, sizeof(msg));

		if (st != 0 || (strcmp("OK", msg) != 0))
			printf("%s\n",msg);;
		
		close(ls);
		closelog();
		return st;
	}

	/* send command to running server */
	syslog(LOG_DEBUG, "cmd=%s", xcmd);
	strcpy(msg, xcmd);
	strcat(msg,"\r\n"); // FIXME: '\r\n'
	
	if (write(ls, msg, strlen(msg)) < 0) {
		syslog(LOG_DEBUG, "client write error: %s", strerror(errno));
		close(ls);
		closelog();
		return EXIT_FAILURE;
	}
	
	n = read(ls, msg, sizeof(msg));
	if (n < 0) {
		syslog(LOG_DEBUG, "client read error: %s", strerror(errno));
	} else
		msg[n]='\0';
	
	if (strcmp("OK", msg) == 0)
		st = 0;
	else if (strcmp("ERR", msg) == 0)
		st = 1;
	else
		printf("%s\n",msg);
	
	close(ls);
	closelog();
	return st;
}

void usage(char *argv[]) {
	fprintf(stderr,
	"Usage: %s [-f][-d][-x cmd]\n"
	"\twhere:\n"
	"\t  -f\t\tdon't detach\n"
	"\t  -d\t\tdebug (implies -f)\n"
	"\t  -x cmd\texecute cmd and quit (implies -f)\n", argv[0]);
	exit(EXIT_FAILURE);
}

/*
 * jc: This daemon previously controled the fan speed, but that is 'sysctrl' daemon job.
 * 
 * This daemon should be just an interface between the linux sysfs interface and the MCU,
 * so, periodicaly:
 * 
 * -read the system temperature from the MCU and write it to /tmp/sys/temp1_input
 * -read /tmp/sys/pwm1 and set the fan speed
 * -update /tmp/sys/fan1_input when the fan speed changes
 * -read /tmp/sys/power_led/trigger and set the power led accordingly
 * -read the power button status from the MCU and generate a key input event
 *  or: update /tmp/sys/power_button with the button present state
 *  or: let sysctrl do it
 * 
 * -Create command table, to simplify adding and invoking commands
 * -use AF_UNIX, providing file based authentication/autorization
 * -add client mode to execute a single command; if the server is running, send it
 *  the command, else send the command directly to the MCU.
 */

int main(int argc, char *argv[]) {
	char response[512];
	int i;
	int st;

	int powerBtn;
	int pressed = 0;
	
	char led_trigger[32];
	int led_brightness;

	char old_temp[16] = "";
	int old_pwm = -1;
	
	int sleepCount = 0;
	int pollTimeMs = 10; // Sleep 10ms for every loop
	char msgBuf[16];
	int pwm;
	
	struct sockaddr_un server;
	struct pollfd *fds = NULL;
	nfds_t nfds = 1;
	
	int retval;
	int ret;
	int msgIdx;
	char message[512];
	char xcmd[64];
		
	stDaemonConfig.goDaemon = 1;
	stDaemonConfig.debug = 0;
	stDaemonConfig.xcmd = 0;
	
	// Parse command line arguments
	while((i = getopt(argc, argv, "fdx:")) != -1) {
		switch(i) {
			case 'f':
				stDaemonConfig.goDaemon = 0;
				break;
			case 'd':
				if (stDaemonConfig.xcmd != 1) {
					stDaemonConfig.debug = 1;
					stDaemonConfig.goDaemon = 0;
				}
				break;
			case 'x':
				if (optarg)
					strcpy(xcmd,optarg);
				else
					usage(argv);
				
				stDaemonConfig.xcmd = 1;
				stDaemonConfig.goDaemon = 0;
				stDaemonConfig.debug = 0;
				break;
			default:
				usage(argv);
		}
	}
	
	// Register some signal handlers
	signal(SIGTERM, quithandler);
	signal(SIGINT, quithandler);
	signal(SIGUSR1, debughandler);
	signal(SIGUSR2, infohandler);
	
	stDaemonConfig.nRetries = 5;
	
	stDaemonConfig.portName = "/dev/ttyS1";
	stDaemonConfig.serverName = "/var/run/dns320l.socket"; // using AF_UNIX

	// Setup syslog

	if (stDaemonConfig.debug)
		setlogmask(LOG_UPTO(LOG_DEBUG));
	else
		setlogmask(LOG_UPTO(LOG_INFO));

	openlog("dns320l-daemon", LOG_CONS, LOG_DAEMON);
	
	if (stDaemonConfig.xcmd == 1)
		exit(client_cmd(xcmd));
		
	if (stDaemonConfig.goDaemon)
		if (st = demonize())
			exit (st);

	// server mode. Open our socket server
	ls = get_socket(&server);
	
	retval = bind(ls, (struct sockaddr *) &server, sizeof(struct sockaddr_un));
	if (retval) {
		syslog(LOG_ERR, "bind : %m");
		cleanup(0, ls,1);
		exit(EXIT_FAILURE);
	}

	retval = listen (ls, 5);
	if (retval) {
		syslog(LOG_ERR, "listen: %m");
		cleanup(0, ls,1);
		exit(EXIT_FAILURE);
	}

	fds = (struct pollfd *)calloc(1,nfds*sizeof(struct pollfd));
	fds->fd = ls;
	fds->events = POLLIN | POLLPRI;
	
	set_serial();
	
	syslog(LOG_INFO, "Server startup success on %s", stDaemonConfig.serverName);
	
	// Send the DeviceReady command to the MCU
	if(SendCommand(fd, DeviceReadyCmd, NULL) != SUCCESS) {
		syslog(LOG_ERR, "Error sending DeviceReady command.");
		//return EXIT_FAILURE; FIXME: can't exit, or init will respanwn it again.
	}
		
	while(1) {
				
		// read desired power led state twice a second
		if(((sleepCount * pollTimeMs) % 500) == 0) {
			if (read_str_from_file(sys_pled_trigger, led_trigger, sizeof(led_trigger)))
				syslog(LOG_ERR, "Error reading led trigger!");
			else {
				if (strcmp(curr_led_trigger, led_trigger)) { // led changed state
					strcpy(curr_led_trigger, led_trigger);
					if (strcmp("heartbeat", led_trigger) == 0 ||
						strcmp("timer", led_trigger) == 0) {
						if (setpowerled_cmd(PwrLedBlinkCmd, msgBuf, sizeof(msgBuf)))
							syslog(LOG_ERR, "Error setting led power blinking!");
						else
							curr_led_brightness = -1;
					}
				}
				
				if (strcmp("none", led_trigger) == 0) {
					if (read_int_from_file(sys_pled_brightness, &led_brightness))
						syslog(LOG_ERR, "Error reading led brightness!");
					else {
						if (curr_led_brightness != led_brightness) { // led changed state
							curr_led_brightness = led_brightness;
							if (led_brightness == 0) {
								if (setpowerled_cmd(PwrLedOffCmd, msgBuf, sizeof(msgBuf)))
									syslog(LOG_ERR, "Error setting led power off!");
							} else if (led_brightness == 1) {
								if (setpowerled_cmd(PwrLedOnCmd, msgBuf, sizeof(msgBuf)))
									syslog(LOG_ERR, "Error setting led power on!");
							}
						}
					}
				}
			}
		}
		
		// read temperature and adjust fan speed every 15 seconds
		if(((sleepCount * pollTimeMs) % 15000) == 0) {
			if (gettemperature_cmd(ThermalStatusGetCmd, msgBuf, sizeof(msgBuf)))
				syslog(LOG_ERR, "Error reading Temperature!");	
			else if (strcmp(old_temp, msgBuf)) {
				syslog(LOG_DEBUG, "temp: %s", msgBuf);
				strcpy(old_temp, msgBuf);
			}
			
			if (read_int_from_file(sys_pwm, &pwm))
				syslog(LOG_ERR, "Error reading pwm!");
			else if (pwm != old_pwm) {
				syslog(LOG_DEBUG, "pwm: %i", pwm);
				old_pwm = pwm;
				if (pwm == 0) {
					if (fanSpeed != 0) 
						setfan_cmd(FanStopCmd, msgBuf, sizeof(msgBuf));
				} else if (pwm < 128) {
					if (fanSpeed != 1)
						setfan_cmd(FanHalfCmd, msgBuf, sizeof(msgBuf));
				} else {
					if (fanSpeed != 2)
						setfan_cmd(FanFullCmd, msgBuf, sizeof(msgBuf));
				}
			}
		}

		sleepCount++;
				
		// sleep, waiting for a client command
		ret = poll(fds, nfds, pollTimeMs); // Time out after pollTimeMs
		
		if (ret == -1) {
			if (errno == EINTR)
				continue;
			syslog(LOG_ERR, "poll: %m");
			exit(EXIT_FAILURE);
		}
		
		for (i = 0; (i < nfds) && (ret); i++) {
			if (!(fds+i)->revents)
				continue;
			ret--;
			
			if (((fds+i)->fd == ls) && ((fds+i)->revents & POLLIN)) {
				/*
				* Accept connection from socket ls:
				* accepted connection will be on socket (fds+nfds)->fd.
				*/
				syslog(LOG_DEBUG, "POLLIN on ls. Accepting connection");
				fds = (struct pollfd *)realloc(fds,(nfds+1)*sizeof(struct pollfd));
				(fds+nfds)->fd  = accept (ls, NULL, 0);
				if ((fds+nfds)->fd == -1) {
					syslog(LOG_ERR, "accept: %m");
					cleanup(0, (fds+nfds)->fd, 1);
					fds = (struct pollfd *)realloc(fds,nfds*sizeof(struct pollfd));
					continue;
				}
				(fds+nfds)->events = POLLIN | POLLRDNORM;
				nfds++;
				continue;
			}
			
			if ((fds+i)->revents & POLLNVAL) {
				syslog(LOG_DEBUG, "POLLNVAL on socket. Freeing resource");
				nfds--;
				memcpy(fds+i,fds+i+1,nfds-i);
				fds = (struct pollfd *)realloc(fds,nfds*sizeof(struct pollfd));
				continue;
			}
			
			if ((fds+i)->revents & POLLHUP) {
				syslog(LOG_DEBUG, "POLLHUP => peer reset connection ...");
				cleanup(0,(fds+i)->fd,2);
				nfds--;
				memcpy(fds+i,fds+i+1,nfds-i);
				fds = (struct pollfd *)realloc(fds,nfds*sizeof(struct pollfd));
				continue;
			}
			
			if ((fds+i)->revents & POLLERR){
				syslog(LOG_DEBUG, "POLLERR => peer reset connection ...");
				cleanup(0,(fds+i)->fd,2);
				nfds--;
				memcpy(fds+i,fds+i+1,nfds-i);
				fds = (struct pollfd *)realloc(fds,nfds*sizeof(struct pollfd));
				continue;
			}
			
			if ((fds+i)->revents & POLLRDNORM) {
				retval = recv((fds+i)->fd, message, sizeof(message)-1, 0); // Don't forget the string terminator here!
				syslog(LOG_DEBUG, "-> (recv) retval = %d.",retval);  /* ped */
				msgIdx = retval;
				if (retval <=0) {
					if (retval == 0) {
						syslog(LOG_DEBUG, "recv()==0 => peer disconnected...");
						cleanup(1,(fds+i)->fd,2);
					} else {
						syslog(LOG_ERR, "receive: %m");
						cleanup( 0, (fds+i)->fd,1);
					}
					nfds--;
					memcpy(fds+i,fds+i+1,nfds-i);
					fds = (struct pollfd *)realloc(fds,nfds*sizeof(struct pollfd));
					continue;
				}
				
				// jc : FIXME: assumes <CR><LF> as EOL.
				while((retval > 0) && (message[msgIdx-2] != '\r') && ((msgIdx+1) < sizeof(message))) {
					retval = recv((fds+i)->fd, &message[msgIdx-2], sizeof(message) - retval - 1, 0);
					syslog(LOG_DEBUG, " \t -> (recv) retval = %d.", retval);
					if(retval > 0)
						msgIdx += retval - 2;
				}
				
				if(msgIdx > 1)
					if(message[msgIdx-1] == '\n')
						if(message[msgIdx-2] == '\r')
							message[msgIdx-2] = '\0';
						else
							message[msgIdx-1] = '\0';

				msgIdx = HandleCommand(message, msgIdx, response, sizeof(response));
				retval = send((fds+i)->fd, response, strlen(response), 0);
				
				if((retval < 0) || (msgIdx > 1)) {
					syslog(LOG_DEBUG, "send()==0 => peer disconnected...");
					cleanup(1,(fds+1)->fd, 2);
				}
				
				if(msgIdx == 3) {
					syslog(LOG_INFO, "Shutting down dns320l-daemon...");
					unlink(stDaemonConfig.serverName);
					return EXIT_SUCCESS;
				}
				continue;
			}
		}
	}
	
	closelog();
	return EXIT_SUCCESS;
}
