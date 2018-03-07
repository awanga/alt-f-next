/*

  Simple system daemon for D-Link DNS-320L

  (c) 2013 Andreas Boehler, andreas _AT_ aboehler.at
  
  2014-2017: Heavily modified and adapted to Alt-F, Joao Cardoso, joao fs cardoso gmail com
   
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
#include <sys/stat.h>
#include <time.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/un.h>
#include <sys/uio.h>
#include <syslog.h>
#include <ctype.h>

#include "dns320l.h"
#include "dns320l-daemon.h"

int ls = -1; // socket descriptor
int fd = -1; // serial descriptor 

#define MAXFDS 10 /* maximum number of connected clients */
struct pollfd fds[MAXFDS]; // simple approach. no need to compact array or grow/shrink it dinamically
int nfds;
	
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

void cleanup(int shut, int sck, int how) {
	int retval;

	if (shut) {
		retval = shutdown(sck, how);
		if (retval == -1)
			syslog(LOG_ERR, "shutdown: %m");
	}
	
	retval = close (sck);
	if (retval)
		syslog(LOG_ERR, "close: %m");
} 

void exit_cleanup() {
	syslog(LOG_INFO, "Exit Handler called");
	close(fd);
	closelog();
	unlink(stDaemonConfig.serverName);
}

static void quithandler(int sig) {
	if (stDaemonConfig.xcmd == 0) {
		syslog(LOG_INFO, "Quit Handler called");
		cleanup(1, ls, SHUT_RDWR);
		exit_cleanup();
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

int bcd2int(n) {
	return (n & 0x0f) + 10 * ((n & 0xf0) >> 4);
}

int int2bcd(n) {
	return ((n / 10) << 4) + (n % 10);
}

void set_serial() {
	struct termios tty;
		
	fd = open (stDaemonConfig.portName, O_RDWR | O_NOCTTY | O_SYNC);
	if (fd < 0) {
		syslog(LOG_ERR, "error opening %s: %m", stDaemonConfig.portName);
		exit(EXIT_FAILURE);
	}
	
	if (lockf(fd, F_TLOCK, 0)) {
		syslog(LOG_ERR, "error locking %s: %m", stDaemonConfig.portName);
		exit(EXIT_FAILURE);
	}
	
	memset (&tty, 0, sizeof tty);

	cfsetspeed (&tty, B115200); // set input and output speed to 115200 bps
	cfmakeraw(&tty); // make raw
	tty.c_cflag |= (CREAD | CLOCAL); // Enable receiver, disable modem control lines, 
	tty.c_cc[VMIN]  = 0; // read does block for VTIME
	tty.c_cc[VTIME] = 1; // 0.1 seconds read timeout

	if (tcsetattr (fd, TCSANOW, &tty) != 0) {
		syslog(LOG_ERR, "error from tcsetattr: %m");
		exit(EXIT_FAILURE); 
	}
}

void ClearSerialPort(int fd) {
	int i, j, n, pollrc;
	char buf[64], msg[64];
	struct pollfd fds[1];

	fds[0].fd = fd;
	fds[0].events = POLLIN;
	pollrc = poll(fds, 1, 0);
	if(pollrc > 0) {
		if(fds[0].revents & POLLIN) {
			do {
				n = read(fd, buf, sizeof(buf));	
				j = 0;
				for (i=0; i<n; i++)
					j += sprintf(&msg[j], "%02x ", buf[i]);
				syslog(LOG_DEBUG, "ClearSerialPort read %d bytes: %s", n, msg);
			} while(n == sizeof(buf));
		}
	}
}

int send_pkt(int fd, char *cmd) {
	int count, i, n;
	char msg[64];
	
	i = 0; n=0;
	do {
		n += sprintf(&msg[n], "%02x ", cmd[i]);
		count = write(fd, &cmd[i], 1);
		i++;
		usleep(100); // The MCU seems to need some time..
		if(count != 1){
			syslog(LOG_ERR, "send_pkt: error writing byte %i err=%i: %s", i-1, count, msg);
			return ERR_WRITE_ERROR;
		}
	} while(cmd[i-1] != CMD_STOP_MAGIC);
	
	
	syslog(LOG_DEBUG, "send_pkt: %s", msg);

	return SUCCESS;
}

int receive_pkt(int fd, char *buf, int bufsize) {
	int i, j, n;
	char msg[64];
	
	i = 0; j = 0;
	do {
		n = read(fd, &buf[i], 1);
		j += sprintf(&msg[j], "%02x ", buf[i]);
		i++;
	} while((n == 1) && (buf[i-1] != CMD_STOP_MAGIC) && i < bufsize);

	syslog(LOG_DEBUG, "rcv_pkt:  %s", msg);
	
	if(buf[i-1] != CMD_STOP_MAGIC){
		syslog(LOG_ERR, "rcv_pkt: no stop magic, but read %i bytes!", i);
		return ERR_WRONG_ANSWER;
	}
	
	return SUCCESS;
}

int CheckResponse(char *cmd, char *resp) {
	int failure, i, n1, n2;
	char msg1[64], msg2[64] ;

	failure = 0;
	for(i = 0; i < 5; i++) {
		if(resp[i] != cmd[i])
			failure = 1;
	}

	if(failure) {
		n1 = 0; n2 = 0;
		syslog(LOG_DEBUG, "CheckResponse mismatch:");
		for(i = 0; i < 5; i++) {
			n1 += sprintf(&msg1[n1], "%02x ", cmd[i]);
			n2 += sprintf(&msg2[n2], "%02x ", resp[i]);
		}
		syslog(LOG_DEBUG, " cmd:  %s", msg1);
		syslog(LOG_DEBUG, " resp: %s", msg2);
		return ERR_WRONG_ANSWER;
	}
	return SUCCESS;
}

int _SendCommand(int fd, char *cmd, char *outArray) {
	int i;
	char buf[16]; // We need to keep the DateAndTime values here
	// Yes, we're sending byte by byte here - b/c the lenght of
	// commands and responses can vary!
	
	ClearSerialPort(fd); // We clear the serial port in case
	// some old data from a previous request is still pending

	if (send_pkt(fd, cmd) != SUCCESS)
		return 1;

	//usleep(20000); // Give the µC some time to answer...

	/* If outArray is not NULL a response is expected */
	if(outArray != NULL) {
		/* get response packet */
		if (receive_pkt(fd, buf, sizeof(buf)) != SUCCESS)
			return ERR_WRONG_ANSWER;
		
		/* the response first 5 bytes should be identical to the command that originate it */
		if (CheckResponse(cmd, buf) != SUCCESS)
			return ERR_WRONG_ANSWER;
		
		/* copy the answer to the outArray */
		for(i = 0; i < sizeof(buf); i++)
			outArray[i] = buf[i];
	}
		
	//usleep(20000); // Give the µC some time to answer...
	
	/* an ack packet should always be received */
	if (receive_pkt(fd, buf, sizeof(buf)) != SUCCESS)
		return ERR_WRONG_ANSWER;
	
	/* and should be an ack */
	if (CheckResponse(AckFromSerial, buf) != SUCCESS)
		return ERR_WRONG_ANSWER;
	
	return SUCCESS;
}

int SendCommand(int fd, char *cmd, char *outArray) {
	int nRetries = 0;
	int ret;

	do {
		ret = _SendCommand(fd, cmd, outArray);
		nRetries++;
		if (ret != SUCCESS)
			syslog(LOG_DEBUG, "SendCommand retry %i", nRetries);
	} while((ret != SUCCESS) && (nRetries <= stDaemonConfig.nRetries));

	return ret;
}

int simple_cmd(char *mcmd, char *retMessage, int retSize) {
	if(SendCommand(fd, mcmd, NULL) != SUCCESS) {
		strncpy(retMessage, "ERR", retSize);
		return 1;
	}

	strncpy(retMessage, "OK", retSize);
	return 0;
}

int simple_cmd2(char *mcmd, char *retMessage, int retSize) {
	char buf[16];
	
	if(SendCommand(fd, mcmd, buf) != SUCCESS) {
		strncpy(retMessage, "ERR", retSize);
		return 1;
	}

	snprintf(retMessage, retSize, "%d", buf[5]);
	return 0;	
}

int setfan_cmd(char *mcmd, char *retMessage, int retSize) {
	char *buf = "0";
	
	if (simple_cmd(mcmd, retMessage, retSize) != SUCCESS) {
		strncpy(retMessage, "ERR", retSize);
		return 1;
	}

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
	strncpy(retMessage, "OK", retSize);
	syslog(LOG_DEBUG, "fan: %s", buf);
	return 0;
}
	
int gettemperature_cmd(char *mcmd, char *retMessage, int retSize) {
	char buf[16];
	int temp;
	
	if(SendCommand(fd, mcmd, buf) != SUCCESS) {
		strncpy(retMessage, "ERR", retSize);
		return 1;
    }
		
	temp = ThermalTable[(int)buf[5]];
	snprintf(retMessage, retSize, "%d", temp*1000);
	write_str_to_file(sys_temp_input, retMessage);
	return 0;
}

int setpowerled_cmd(char *mcmd, char *retMessage, int retSize) {
	if (simple_cmd(mcmd, retMessage, retSize) != 0) {
		strncpy(retMessage, "ERR", retSize);
		return 1;
	}
	
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
	strncpy(retMessage, "OK", retSize);
	return 0;
}

/* RTC date/time is in UTC */
int systohc_cmd(char *mcmd, char *retMessage, int retSize) {
	 char cmdBuf[16];
	 time_t sysTime;
	 struct tm *strSetTime;
	 int i;
	
    for(i = 0; i < 13; i++)
      cmdBuf[i] = mcmd[i];
	
    sysTime = time(NULL); // get current time
    strSetTime = gmtime(&sysTime); // convert to UTC
    // put it into the command buffer
    cmdBuf[5] = (char)strSetTime->tm_sec;
    cmdBuf[6] = (char)strSetTime->tm_min;
    cmdBuf[7] = (char)strSetTime->tm_hour;
    cmdBuf[8] = (char)strSetTime->tm_wday;
    cmdBuf[9] = (char)strSetTime->tm_mday;
    cmdBuf[10] = (char)(strSetTime->tm_mon + 1);
    cmdBuf[11] = (char)(strSetTime->tm_year - 100);

	// And modify the values so that the MCU understands them...
	for(i = 5; i < 12; i++)
		cmdBuf[i] = int2bcd(cmdBuf[i]);

	if(SendCommand(fd, cmdBuf, NULL) != SUCCESS) {
		strncpy(retMessage, "ERR", retSize);
		return 1;
	}
		
	strncpy(retMessage, "OK", retSize);
	return 0;
}

/* RTC date/time is in UTC */
int hctosys_cmd(char *mcmd, char *retMessage, int retSize) {
	struct tm strTime;
	struct timeval setTime;
	time_t rtcTime;
	time_t sysTime;
	char timeStr[100];
	char buf[16];
	int i;
	
    if(SendCommand(fd, RDateAndTimeCmd, buf) != SUCCESS) {
		strncpy(retMessage, "ERR", retSize);
		return 1;
    }

	for(i = 5; i < 12; i++)
		buf[i] = bcd2int(buf[i]);

	strTime.tm_year = (100 + (int)buf[11]);
	strTime.tm_mon = buf[10] - 1;
	strTime.tm_mday = buf[9];
	strTime.tm_hour = buf[7];
	strTime.tm_min = buf[6];
	strTime.tm_sec = buf[5];
	strTime.tm_isdst = -1;

	rtcTime = timegm(&strTime);
	strcpy(timeStr, ctime(&rtcTime));
	// Retrieve system time
	sysTime = time(NULL);
	setTime.tv_sec = rtcTime;
	setTime.tv_usec = 0;
	// Set the time and print the difference on success
	if(settimeofday(&setTime, NULL) != 0)
		strncpy(retMessage, "ERR", retSize);
	else
		snprintf(retMessage, retSize, "%sSys: %sDiff: %.fs",
				 timeStr, ctime(&sysTime), difftime(sysTime, rtcTime));
	return 0;
}

/* RTC date/time is in UTC */
int readrtc_cmd(char *mcmd, char *retMessage, int retSize) {
	struct tm strTime;
	time_t rtcTime;
	char timeStr[100];
	char buf[16];
	int i;
	
    if(SendCommand(fd, mcmd, buf) != SUCCESS) {
		strncpy(retMessage, "ERR", retSize);
		return 1;
	}

	for(i = 5; i < 12; i++)
		buf[i] = bcd2int(buf[i]);

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
	snprintf(retMessage, retSize, "%s", timeStr);
	return 0;
}

int readalarm( int *month, int *day, int *hour, int *min ) {
	char buf[16];

	if (SendCommand(fd, RAlarmMonthCmd, buf) != SUCCESS)
		 return 1;
	*month = bcd2int(buf[5]);

	if (SendCommand(fd, RAlarmDateCmd, buf) != SUCCESS)
		return 1;
	*day = bcd2int(buf[5]);

	if (SendCommand(fd, RAlarmHourCmd, buf) != SUCCESS)
		return 1;
	*hour = bcd2int(buf[5]);

	if (SendCommand(fd, RAlarmMinuteCmd, buf) != SUCCESS)
		return 1;	
	*min = bcd2int(buf[5]);
	
	syslog(LOG_DEBUG, "alarm read:  %d %d %d %d\n", *month, *day, *hour, *min);
	
	return 0;
}

int writealarm( int month, int day, int hour, int min) {
	
	syslog(LOG_DEBUG, "alarm write: %d %d %d %d", month + 1, day, hour, min);
	
	WAlarmMonthCmd[5]= int2bcd(month + 1);
	if (SendCommand(fd, WAlarmMonthCmd, NULL) != SUCCESS)
		 return 1;

	WAlarmDateCmd[5] = int2bcd(day);
	if (SendCommand(fd, WAlarmDateCmd, NULL) != SUCCESS)
		return 1;

	WAlarmHourCmd[5] = int2bcd(hour);
	if (SendCommand(fd, WAlarmHourCmd, NULL) != SUCCESS)
		return 1;

	WAlarmMinuteCmd[5] = int2bcd(min);
	if (SendCommand(fd, WAlarmMinuteCmd, NULL)  != SUCCESS)
		return 1;
	
	return 0;
}

/* MCU alarm date/time is in UTC */
/* returns 0 on sucess, 1 on error, 2 on elapsed alarm, 3 on disabled alarm */
int readAlarm_cmd( char *mcmd, char *retMessage, int retSize) {
	int ret, year, month=-1, day=-1, hour=-1, min=-1;
	char *elapsed = " ";

	if (readalarm( &month, &day,  &hour, &min))
		goto err;
	
	if (day == 0 && month == 0 && hour == 0 && min == 0) {
		simple_cmd(WAlarmDisableCmd, retMessage, retSize);
		snprintf(retMessage, retSize, "Wakeup alarm disabled");
		return 3;
	}
	
	simple_cmd(WAlarmEnableCmd, retMessage, retSize);
	
	struct tm tm, *otm;
	time_t utime, ltime;

	/* get current year */
	ltime = time(NULL);
	otm = localtime(&ltime);
	year = otm->tm_year;

	tm.tm_sec = 0;
	tm.tm_min = min;
	tm.tm_hour = hour;
	tm.tm_mday = day;
	tm.tm_mon = month - 1;
	tm.tm_year = year;
	tm.tm_isdst = -1;

	utime = timegm(&tm);
	if (utime == -1)
		goto err;
	
	ret = 0;
	if (ltime > utime) {
		elapsed = " (elapsed) ";
		ret = 2;
	}

	otm = localtime(&utime);
	
	char buf[64];
	strftime(buf, sizeof(buf), "%F %R", otm);
	snprintf(retMessage, retSize, "Wakeup alarm%sset to: %s", elapsed, buf);
	
	return ret;

err:
	snprintf(retMessage, retSize, "ERR %d/%d %d:%d", month, day, hour, min);
	return 1;
}

/* MCU alarm date/time is in UTC, user specified date/time is in localtime */
/* retMessage contains command option string on entry */
int writeAlarm_cmd( char *mcmd, char *retMessage, int retSize) {
	int i, disable_alarm = 0, ndays = 0, nmonth = 0, year, month=-1, day=-1, hour=-1, min=-1;
	char *ptr, *eptr;
	time_t utime;
	struct tm *otm, itm = {0, 0, 0, 0, -1, 0, 0, 0, 0}; // default values to disable alarm 

	/* get localtime */
	utime = time(NULL);
	otm = localtime(&utime);
	year = otm->tm_year;

	ptr = retMessage;
	if (strncasecmp(ptr, "now", 3) == 0) {
		month = otm->tm_mon + 1;
		day = otm->tm_mday;
		hour = otm->tm_hour;
		min = otm->tm_min + 3;
	} else if (strncasecmp(ptr, "disable", 7) == 0) {
		disable_alarm = 1;
	} else if (retMessage[0] == '+') { // +0 sets to current time
		i = strtol(ptr, &eptr, 10); if (ptr == eptr) goto err; ptr=eptr;
		if (*ptr == 'm')
			nmonth = i;
		else if (*ptr == 'd')
			ndays = i;
		else
			goto err; 
		if (readalarm(&month, &day, &hour, &min))
			goto err;
		if (day == 0 && month == 0 && hour == 0 && min == 0) { // alarm was disabled
			month = otm->tm_mon + 1;
			day = otm->tm_mday;
			hour = otm->tm_hour;
			min = otm->tm_min + 3;
		}
		day += ndays; // adjusted by mktime latter
		month += nmonth; // adjusted by mktime latter
	} else {
		month = strtol(ptr, &eptr, 10);  if (ptr == eptr) goto err; ptr=eptr;
		day = strtol(ptr, &eptr, 10); if (ptr == eptr) goto err; ptr=eptr;
		hour = strtol(ptr, &eptr, 10);  if (ptr == eptr) goto err; ptr=eptr;
		min = strtol(ptr, &eptr, 10);  if (ptr == eptr) goto err; ptr=eptr;
		
		if (day < 1 || day > 31 || month < 1 || month > 12 || hour < 0 || hour > 23 || min < 0 || min > 59)
			goto err;
	}

	if (disable_alarm) {
		otm = &itm;
	} else {
		/* user input local date/time, convert to UTC */
		itm.tm_sec = 0;
		itm.tm_min = min;
		itm.tm_hour = hour;
		itm.tm_mday = day;
		itm.tm_mon = month - 1;
		itm.tm_year = year;
		itm.tm_isdst = -1;
		
		utime = mktime(&itm); // localtime tm to UTC time_t
		if ( utime == -1)
			goto err;

		otm = gmtime(&utime); // time_t to UTC tm, save this in MCU
		if (otm == NULL)
			goto err;
	}

	if (writealarm( otm->tm_mon, otm->tm_mday, otm->tm_hour, otm->tm_min))
		goto err;
	
	return readAlarm_cmd(NULL, retMessage, retSize);
	
err:
	snprintf(retMessage, retSize, "ERR WriteAlarm: month day hour min | +N{d|m} (days|month) | now | disable");
	return 1;
}

int deviceshutdown_cmd( char *mcmd, char *retMessage, int retSize) {
	int delay;
	char *eptr;
	
	delay = strtol(retMessage, &eptr, 10);
	if (eptr == retMessage) {
		//snprintf(retMessage, retSize, "ERR seconds (using 5)");
		//return 1;
		delay = 5; // default in case of error
	}
	
	DeviceShutdownCmd[5] = int2bcd(delay);
	return simple_cmd(DeviceShutdownCmd, retMessage, retSize);
}

int shutdowndaemon_cmd( char *mcmd, char *retMessage, int retSize) {
    strncpy(retMessage, "OK", retSize);
    return -2;
}

int quit_cmd(char *mcmd, char *retMessage, int retSize) {
    strncpy(retMessage, "Bye", retSize);
    return -1;
  }
  
int help_cmd(char *mcmd, char *retMessage, int retSize) {
	int i;
	
	strncpy(retMessage, "Available Commands:\n\n", retSize);
	for (i = 0; i < sizeof(cmds)/sizeof(cmd_t); i++) {
		strncat(retMessage, cmds[i].ucmd, retSize);
		strncat(retMessage, ", ", retSize);
	}
	retMessage[strlen(retMessage)-2] = 0;
	strncat(retMessage, ".", retSize);
	return 1;
}

/* retMessage can be command options on entry and return message on exit */
int HandleCommand(char *cmd, int cmdLen, char *retMessage, int retSize) {
	int i, j;
	char *te;
	
	/* deserialize: in server mode, command args follow command, split it */
	te = index(cmd, ' ');
	if (te != NULL) {
		*te = '\0';
		j = strlen(cmd);
		strcpy(retMessage, &cmd[j+1]);
	}
	
	for (i = 0; i < sizeof(cmds)/sizeof(cmd_t); i++) {

		if (strcasecmp(cmds[i].ucmd, cmd) == 0) {
			syslog(LOG_INFO, "Handling Command: \"%s\" opts=\"%s\"", cmds[i].ucmd, retMessage);
			if(cmds[i].func != NULL)
				return cmds[i].func(cmds[i].mcmd, retMessage, retSize);
		}
	}
	sprintf(retMessage,"ERR Unknown command \"%s\"", cmd);
	syslog(LOG_INFO, "Unknown Command: %s", cmd);
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
	/* if launched by init, can't fork, or its pid will change and it will be respanwned by init */
	if (getppid() != 1) {
		pid_t pid = fork();
		if (pid != 0) // parent
			exit(0);
		setsid();
	}

	umask(0);
	
	if((chdir("/")) < 0) {
		syslog(LOG_ERR, "Could not chdir: %m");
		exit(EXIT_FAILURE);
	}

	/* redirect stdin/out/err */
	freopen("/dev/null", "r", stdin);
	freopen("/dev/null", "w", stdout);
	freopen("/dev/null", "w", stderr);
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

void start_listening(struct sockaddr_un *server) {
	int retval;
	
	retval = bind(ls, (struct sockaddr *) server, sizeof(struct sockaddr_un));
	if (retval) {
		syslog(LOG_ERR, "bind : %m");
		exit(EXIT_FAILURE);
	}

	if (chmod(stDaemonConfig.serverName, S_IRUSR | S_IWUSR)) {
		syslog(LOG_ERR, "chmod: %m");
		exit(EXIT_FAILURE);
	}

	retval = listen (ls, MAXFDS);
	if (retval) {
		syslog(LOG_ERR, "listen: %m");
		exit(EXIT_FAILURE);
	}
}

void poll_setup() {
	int i;
	memset(fds, 0, sizeof(fds));
	for( i = 0; i < MAXFDS; i++)
		fds[i].fd = -1;

	fds[0].fd = ls;
	fds[0].events = POLLIN;
	nfds = 1;
}

void poll_wait(int ms) {
	int i, j, nev, retval;
	char message[512] = "\0";
	char response[512] = "\0";
	int msgIdx;
	
	// sleep, waiting for a client command
	nev = poll(fds, MAXFDS, ms); // MAXFD is a small number, 10
	if (nev == 0)
		return;
	
	if (nev == -1) {
		if (errno == EINTR)
			return;
		syslog(LOG_ERR, "poll: %m");
		exit(EXIT_FAILURE);
	}
	
	syslog(LOG_DEBUG, "poll:  nfds=%d nev=%d", nfds, nev);
	
	for (i = 0; i < MAXFDS && nev != 0; i++) {
		if (fds[i].fd == -1 || fds[i].revents == 0)
			continue;
		nev--; // avoid iterating array if all events have already been processed
		
		syslog(LOG_DEBUG, "  i=%d fd=%d ev=%02x", i, fds[i].fd, fds[i].revents);
		
			/* someone called, accept connection */
		if (fds[i].revents & POLLIN && i == 0) {
			if (nfds == MAXFDS) { // no fds space left
				syslog(LOG_DEBUG, "-> delaying nfds=%d", nfds);
				continue;
			}

			for (j = 1; j < MAXFDS; j++)
				if (fds[j].fd == -1)
					break;
			fds[j].fd  = accept (ls, NULL, NULL);
			syslog(LOG_DEBUG, "-> accept nfds=%d j=%d fd=%d", nfds, j, fds[j].fd);				
			if (fds[j].fd == -1) {
				syslog(LOG_ERR, "accept: %m");
				continue;
			}
			fds[j].events = POLLIN;
			fds[j].revents = 0; // this is needed, this array item might be processed next in the loop
			nfds++;
			continue;
		}
		
			/* There is client data to read */
		if (fds[i].revents & POLLIN) {
			retval = recv( fds[i].fd, message, sizeof(message), 0);
			syslog(LOG_DEBUG, "-> recv i=%d fd=%d retval=%d: \"%s\"", i, fds[i].fd, retval, message);
			msgIdx = retval;
			if (retval <= 0) {
				if (retval == 0)  /* peer has performed an orderly shutdown */
					syslog(LOG_DEBUG, "   peer disconnected");
				else  /* error */
					syslog(LOG_ERR, "recv: %m");
				
				cleanup(1, fds[i].fd, SHUT_RDWR);  /* No more receptions or transmissions.  */
				fds[i].fd = -1;
				nfds--;
				continue;
			}

			/* this *assumes* commands are short and fit a single buffer, and are not transmition
				* fragmented, so no need to further recv() while !EOL */
			if (message[msgIdx-1] != '\n')
				syslog(LOG_ERR, "breaked assumption!");
			
			message[msgIdx-1] = '\0';
			msgIdx = HandleCommand( message, msgIdx, response, sizeof(response));
			retval = send( fds[i].fd, response, strlen(response), 0);
			response[0] = '\0';
			syslog(LOG_DEBUG, "   send i=%d fd=%d retval=%d", i, fds[i].fd, retval);
			
			/* quit command returns -1 */
			if((retval < 0) || (msgIdx == -1))
				cleanup(1, fds[i].fd, SHUT_RDWR); /* No more receptions or transmissions.  */

			/* shutdown daemon command returns -2 */
			if(msgIdx == -2) {
				syslog(LOG_INFO, "Shutting down dns320l-daemon...");
				exit(EXIT_SUCCESS);
			}
			continue;
		}
		
		/* on termination, some progs send POLIN | POLLHUP, others just POLLHUP */
		if (fds[i].revents & (POLLHUP | POLLERR | POLLNVAL) ) {
			syslog(LOG_DEBUG, "-> hang i=%d fd=%d ev=%02x", i, fds[i].fd, fds[i].revents);
			if (fds[i].revents & (POLLHUP | POLLERR))
				cleanup(1, fds[i].fd, SHUT_RDWR);
			fds[i].fd = -1;
			nfds--;
			continue;
		}
	}
}

/* in xcmd mode, if another instance is already listening on socket
 * go to client mode and send the command to it;
 * If no other instance is listening send the command directly to the MCU
 */
int client_cmd(char *xcmd, char *opt) {
	
	struct sockaddr_un server;
	int ls, st = 0;
	
	char msg[512] = "\0";
	int n;
	
	syslog(LOG_DEBUG, "client_cmd: xcmd=\"%s\" opt=\"%s\"", xcmd, opt);
		
	ls = get_socket(&server);

	if (connect(ls, (struct sockaddr *) &server, sizeof(struct sockaddr_un)) == -1) {
		/* no running server, send command to MCU*/

		syslog(LOG_INFO, "No server, send cmd directly to MCU");
		set_serial();
		if (opt != NULL)
			strcpy(msg, opt);
		st = HandleCommand(xcmd, strlen(xcmd), msg, sizeof(msg));

		if (strncmp("ERR", msg, 3) == 0)
			st = 1;

		printf("%s\n",msg);
		
		cleanup(1, ls, SHUT_WR);
		close(fd);
		closelog();
		return st;
	}

	/* send command to running server */
	if (opt == NULL)
		sprintf(msg, "%s\n", xcmd);
	else
		sprintf(msg, "%s %s\n", xcmd, opt);
	
	if (write(ls, msg, strlen(msg)) < 0) {
		syslog(LOG_DEBUG, "client write error: %s", strerror(errno));
		cleanup(1, ls, SHUT_RDWR);
		closelog();
		return EXIT_FAILURE;
	}

	n = read(ls, msg, sizeof(msg));
	if (n < 0) {
		syslog(LOG_DEBUG, "client read error: %s", strerror(errno));
	} else
		msg[n]='\0';

	st = 0;
	if (strncmp("OK", msg, 2) == 0)
		st = 0;
	else if (strncmp("ERR", msg, 3) == 0)
		st = 1;
		
	printf("%s\n",msg);
	
 	cleanup(1, ls, SHUT_RDWR);
	closelog();
	return st;
}

// read desired power led state and set it if changed
void readset_powerled() {
	char led_trigger[32];
	char msgBuf[16];
	int led_brightness;
	
	if (read_str_from_file(sys_pled_trigger, led_trigger, sizeof(led_trigger))) {
		syslog(LOG_ERR, "Error reading led trigger!");
		return;
	}

	if (strcmp(curr_led_trigger, led_trigger)) { // led changed state
		strcpy(curr_led_trigger, led_trigger);
		if (strcmp("heartbeat", led_trigger) == 0 || strcmp("timer", led_trigger) == 0) {
			if (setpowerled_cmd(PwrLedBlinkCmd, msgBuf, sizeof(msgBuf)))
				syslog(LOG_ERR, "Error setting led power blinking!");
			else
				curr_led_brightness = -1;
		}
	}
	
	if (strcmp("none", led_trigger) == 0) {
		if (read_int_from_file(sys_pled_brightness, &led_brightness)) {
			syslog(LOG_ERR, "Error reading led brightness!");
			return;
		}
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

// read temperature and desired fan speed and update if necessary /tmp/sys/
void readset_temp() {
	char msgBuf[16];
	static char old_temp[16] = "";
	static int old_pwm = -1;
	int pwm;
		
	if (gettemperature_cmd(ThermalStatusGetCmd, msgBuf, sizeof(msgBuf)))
		syslog(LOG_ERR, "Error reading Temperature!");	
	else if (strcmp(old_temp, msgBuf)) {
		syslog(LOG_DEBUG, "temp: %s", msgBuf);
		strcpy(old_temp, msgBuf);
	}
	
	if (read_int_from_file(sys_pwm, &pwm)) {
		syslog(LOG_ERR, "Error reading pwm!");
		return;
	}
	
	if (pwm != old_pwm) {
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
		
void usage(char *argv[]) {
	fprintf(stderr,
	"Usage: %s [-f][-d][-x cmd]\n"
	"\twhere:\n"
	"\t  -f\t\tdon't detach\n"
	"\t  -d\t\tdebug\n"
	"\t  -x cmd\texecute cmd and quit (try -x help)\n", argv[0]);
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
	int i;
	int sleepCount = 0;

	struct sockaddr_un server;
	int pollTimeMs = 10; // Sleep 10ms

	char *xopt = NULL;
	char xcmd[64];

	stDaemonConfig.nRetries = 2;
	stDaemonConfig.portName = "/dev/ttyS1";
	stDaemonConfig.serverName = "/var/run/dns320l.socket"; // using AF_UNIX
	// with telnet or nc (busybox netcat) use local:/var/run/dns320l.socket 

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
				stDaemonConfig.debug = 1;
				break;
				
			case 'x':
				if (optarg)
					strcpy(xcmd,optarg);
				else
					usage(argv);
				
				stDaemonConfig.xcmd = 1;
				stDaemonConfig.goDaemon = 0;
				break;
				
			default:
				usage(argv);
		}
	}
	if (optind < argc) { /* eventual args to command */
		int n = 0;
		xopt = (char *) malloc(64);
		for (i = optind; i < argc && n < 64; i++)
			n += sprintf(&xopt[n], "%s ", argv[i]);
	}
//	printf("xcmd=%s xop=\"%s\" optind=%d argc=%d\n", xcmd, xopt, optind, argc);
	
	// Register some signal handlers
	signal(SIGTERM, quithandler);
	signal(SIGINT, quithandler);
	signal(SIGUSR1, debughandler);
	signal(SIGUSR2, infohandler);
	signal(SIGHUP, SIG_IGN);
	signal(SIGPIPE, SIG_IGN); /* send() */

	// Setup syslog
	if (stDaemonConfig.debug)
		setlogmask(LOG_UPTO(LOG_DEBUG));
	else
		setlogmask(LOG_UPTO(LOG_INFO));

	openlog("dns320l-daemon", LOG_CONS, LOG_DAEMON);
	
	if (stDaemonConfig.xcmd == 1)
		exit(client_cmd(xcmd, xopt));
		
	if (stDaemonConfig.goDaemon)
		demonize();

	// server mode
	set_serial();

	//Open our socket server
	ls = get_socket(&server);
	start_listening(&server);

	// some cleanup on exit. after bind()
	atexit(exit_cleanup);

	poll_setup();
	
	syslog(LOG_INFO, "Server startup success on %s", stDaemonConfig.serverName);
	
	// Send the DeviceReady command to the MCU
	if(SendCommand(fd, DeviceReadyCmd, NULL) != SUCCESS) {
		syslog(LOG_ERR, "Error sending DeviceReady command.");
		//return EXIT_FAILURE; FIXME: can't exit, or init will respanwn it again.
	}
		
	while(1) {	
		// read desired power led state twice a second
		if(((sleepCount * pollTimeMs) % 500) == 0)
			readset_powerled();
		
		// read temperature and adjust fan speed every 15 seconds
		if(((sleepCount * pollTimeMs) % 15000) == 0)
			readset_temp();

		sleepCount++;
				
		// sleep, waiting for a client command
		poll_wait(pollTimeMs);
	}
	return EXIT_SUCCESS;
}
