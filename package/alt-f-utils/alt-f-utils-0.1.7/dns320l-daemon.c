/*

  Simple system daemon for D-Link DNS-320L

  (c) 2013 Andreas Boehler, andreas _AT_ aboehler.at
  
  Modified and adapted to Alt-F by Joao Cardoso, joao fs cardoso gmail com

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
#include <time.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/un.h>
#include <sys/uio.h>
#include <syslog.h>
#include <ctype.h>

#include "dns320l.h"
#include "dns320l-daemon.h"

int ls;
int fd;

DaemonConfig stDaemonConfig;

int fanSpeed = -1; // global to keep fan synchronized between user commands and main() fancontrol
  
/** @file dns320l-daemon.c
    @brief Implementation of a free system daemon replacement for
           the D-Link DNS-320L NAS
    @author Andreas Boehler, andreas _AT_ aboehler.at
    @version 1.0
    @date 2013/09/12
*/


int gpio_get_value(unsigned int gpio, unsigned int *value)
{
  int fd, len;
  char buf[100];
  char ch;

  len = snprintf(buf, sizeof(buf), "%s/gpio%d/value", stDaemonConfig.gpioDir, gpio);

  fd = open(buf, O_RDONLY);
  if (fd < 0) {
    syslog(LOG_ERR, "gpio/get-value");
    return fd;
  }

  read(fd, &ch, 1);

  if (ch != '0') {
    *value = 1;
  } else {
    *value = 0;
  }

  close(fd);
  return 0;
}

void cleanup(int shut,int s,int howmany)
{
  int     retval;

  /*
   * Shutdown and close sock1 completely.
   */
  if (shut)
  {
    retval = shutdown(s,howmany);
    if (retval == -1)
      syslog(LOG_ERR, "shutdown");
  }
  retval = close (s);
  if (retval)
    syslog(LOG_ERR, "close");
} 

static void sighandler(int sig)
{
  syslog(LOG_DEBUG, "Signal Handler called");
  cleanup(0, ls, 1);
  unlink(stDaemonConfig.serverName);
  exit(EXIT_SUCCESS);
}

int set_interface_attribs (int fd, int speed, int parity)
{
  struct termios tty;
  memset (&tty, 0, sizeof tty);
  if (tcgetattr (fd, &tty) != 0)
  {
    syslog(LOG_ERR, "error %d from tcgetattr", errno);
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

  if (tcsetattr (fd, TCSANOW, &tty) != 0)
  {
    syslog(LOG_ERR, "error %d from tcsetattr", errno);
    return -1;
  }
  return 0;
}

void set_blocking (int fd, int should_block)
{
  struct termios tty;
  memset (&tty, 0, sizeof tty);
  if (tcgetattr (fd, &tty) != 0)
  {
    syslog(LOG_ERR, "error %d from tggetattr", errno);
    return;
  }

  tty.c_cc[VMIN]  = should_block ? 1 : 0;
  tty.c_cc[VTIME] = 5;            // 0.5 seconds read timeout

  if (tcsetattr (fd, TCSANOW, &tty) != 0)
    syslog(LOG_ERR, "error %d setting term attributes", errno);
}

int CheckResponse(char *buf, char *cmd, int len)
{
  int i;
  int failure = 0;

  // Attention, 5 is hardcoded here and never checked!
  for(i=0;i<5;i++)
  {
    if(buf[i] != cmd[i])
    {
      syslog(LOG_ERR, "Char %i is %i but should be %i", i, buf[i], cmd[i]);
      failure = 1;
      break;
    }
  }
  if(failure)
  {
    for(i=0;i<len;i++)
    {
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

void ClearSerialPort(int fd)
{
  char buf[100];
  struct pollfd fds[1];
  fds[0].fd = fd;
  fds[0].events = POLLIN;
  int n = 0;
  int pollrc;
  pollrc = poll(fds, 1, 0);
  if(pollrc > 0)
  {
    if(fds[0].revents & POLLIN)
    {
      syslog(LOG_DEBUG, "Clearing Serial Port...");
      do
      {
        n = read(fd, buf, sizeof(buf));
      } while(n == sizeof(buf));
    }
  }
}

int SendCommand(int fd, char *cmd, char *outArray)
{
  int nRetries = -1;
  int ret;
  do
  {
    ret = _SendCommand(fd, cmd, outArray);
    nRetries++;
	syslog(LOG_DEBUG, "Try number: %i", nRetries+1);
  } while((ret != SUCCESS) && (nRetries < stDaemonConfig.nRetries));

  return ret;
}

int _SendCommand(int fd, char *cmd, char *outArray)
{
  int n;
  int i;
  int j;
  ssize_t count;

  char buf[15]; // We need to keep the DateAndTime values here
  // Yes, we're sending byte by byte here - b/c the lenght of
  // commands and responses can vary!

  ClearSerialPort(fd); // We clear the serial port in case
  // some old data from a previous request is still pending

  i=0;
  do
  {
    count = write(fd, &cmd[i], 1);
    i++;
    usleep(100); // The MCU seems to need some time..
    if(count != 1)
    {
      syslog(LOG_ERR, "Error writing byte %i: %i, count: %i", (i-1), cmd[i-1], count);
      return ERR_WRITE_ERROR;
    }
  } while(cmd[i-1] != CMD_STOP_MAGIC);

  i=0;
  do
  {
    n = read(fd, &buf[i], 1);
    i++;
  } while((n == 1) && (buf[i-1] != CMD_STOP_MAGIC));


  if(buf[i-1] != CMD_STOP_MAGIC)
  {
    syslog(LOG_ERR, "Got no stop magic, but read %i bytes!", i);
    for(j=0;j<i;j++)
    {
      syslog(LOG_DEBUG, "Buf %i: %i", j, buf[j]);
    }
    return ERR_WRONG_ANSWER;
  }
  else
  {
    // If outArray is not NULL, an answer was requested
    if(outArray != NULL)
    {
      if(CheckResponse(buf, cmd, i) != SUCCESS)
      {
        return ERR_WRONG_ANSWER;
      }
      // Copy the answer to the outArray
      for(j=0; j<i; j++)
      {
        outArray[j] = buf[j];
      }
      usleep(20000); // Give the µC some time to answer...

      // Wait for ACK from Serial
      i=0;
      do
      {
        n = read(fd, &buf[i], 1);
        i++;
      } while((n == 1) && (buf[i-1] != CMD_STOP_MAGIC));


      if(buf[i-1] != CMD_STOP_MAGIC)
      {
        syslog(LOG_ERR, "Got no stop magic!");
        for(j=0;j<i;j++)
        {
         syslog(LOG_DEBUG, "Buf %i: %i", j, buf[j]);
        }

        return ERR_WRONG_ANSWER;
      }

      CheckResponse(buf, AckFromSerial, i);
      syslog(LOG_DEBUG, "Returning %i read bytes", n);
      return SUCCESS;
    }
    // Only wait for ACK if no response is expected
    else
    {
      return CheckResponse(buf, AckFromSerial, i);
    }
  }
}

int simple_cmd(char *mcmd, char *retMessage, int bufSize) {
	if(SendCommand(fd, mcmd, NULL) == SUCCESS) {
		strncpy(retMessage, "OK\n", bufSize);
	} else {
		strncpy(retMessage, "ERR\n", bufSize);
		return 1;
	}
	return 0;
}

int simple_cmd2(char *mcmd, char *retMessage, int bufSize) {
	char buf[15];
	int len;
	
	if(SendCommand(fd, mcmd, buf) > ERR_WRONG_ANSWER) {
		snprintf(retMessage, bufSize, "%d", buf[5]);
		len = strlen(retMessage);
		if(bufSize > 1) {
			retMessage[len] = '\n';
			retMessage[len+1] = '\0';
		}
	} else {
		strncpy(retMessage, "ERR\n", bufSize);
		return 1;
	}
	return 0;
}

int setfan_cmd(char *mcmd, char *retMessage, int bufSize) {
	if (simple_cmd(mcmd, retMessage, bufSize) == 0) {
		switch (mcmd[3]) {
			case 0:
				write_str_to_file("/tmp/sys/fan1_input", "0");
				fanSpeed = 0;
				break;
			case 1:
				write_str_to_file("/tmp/sys/fan1_input", "3000");
				fanSpeed = 1;
				break;
			case 2:
				write_str_to_file("/tmp/sys/fan1_input", "6000");
				fanSpeed = 2;
				break;
		}
		return 0;
	}
	return 1;
}
	
int gettemperature_cmd(char *mcmd, char *retMessage, int bufSize) {
	char buf[15];
	int tmp;
	int len;
  
	if(SendCommand(fd, mcmd, buf) > ERR_WRONG_ANSWER) {
      tmp = ThermalTable[(int)buf[5]];
      snprintf(retMessage, bufSize, "%d", tmp);
      len = strlen(retMessage);
      if(bufSize > 1) {
        retMessage[len] = '\n';
        retMessage[len+1] = '\0';
      }
      write_str_to_file("/tmp/sys/temp1_input", retMessage);
    } else {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  return 0;
}

int systohc_cmd(char *mcmd, char *retMessage, int bufSize) {
	 char cmdBuf[15];
	 time_t sysTime;
	 struct tm *strSetTime;
	 int i;
	
    for(i=0;i<13;i++)
      cmdBuf[i] = mcmd[i];
	
    sysTime = time(NULL);
    strSetTime = localtime(&sysTime);
    // Put the current local time into the command buffer
    cmdBuf[5] = (char)strSetTime->tm_sec;
    cmdBuf[6] = (char)strSetTime->tm_min;
    cmdBuf[7] = (char)strSetTime->tm_hour;
    cmdBuf[8] = (char)strSetTime->tm_wday;
    cmdBuf[9] = (char)strSetTime->tm_mday;
    cmdBuf[10] = (char)(strSetTime->tm_mon + 1);
    cmdBuf[11] = (char)(strSetTime->tm_year - 100);

	// And modify the values so that the MCU understands them...
    for(i=5;i<12;i++)
      cmdBuf[i] = ((cmdBuf[i] / 10) << 4) + (cmdBuf[i] % 10);

    if(SendCommand(fd, cmdBuf, NULL) == SUCCESS)
      strncpy(retMessage, "OK\n", bufSize);
    else {
      strncpy(retMessage, "ERR\n", bufSize);
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
	char buf[15];
	int i;
	
    if(SendCommand(fd, RDateAndTimeCmd, buf) > ERR_WRONG_ANSWER) {
      for(i=5;i<12;i++)
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
      // Retrieve system time
      sysTime = time(NULL);
      setTime.tv_sec = rtcTime;
      setTime.tv_usec = 0;
      // Set the time and print the difference on success
      if(settimeofday(&setTime, NULL) != 0)
        strncpy(retMessage, "ERR\n", bufSize);
      else
        snprintf(retMessage, bufSize, "RTC: %sSys: %sDiff: %.fs\n", timeStr, ctime(&sysTime), difftime(sysTime, rtcTime));
    } else {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
    return 0;
}

int readrtc_cmd(char *mcmd, char *retMessage, int bufSize) {
	struct tm strTime;
	time_t rtcTime;
	char timeStr[100];
	char buf[15];
	int i;
	
    if(SendCommand(fd, mcmd, buf) > ERR_WRONG_ANSWER) {
      for(i=5;i<12;i++)
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
      snprintf(retMessage, bufSize, "RTC: %s", timeStr);
    } else {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
    return 0;
}

int shutdowndaemon_cmd(char *mcmd, char *retMessage, int bufSize) {
    strncpy(retMessage, "OK\n", bufSize);
    return 3;
}

int quit_cmd(char *mcmd, char *retMessage, int bufSize) {
    strncpy(retMessage, "Bye\n", bufSize);
    return 2;
  }
  
int help_cmd(char *mcmd, char *retMessage, int bufSize) {
	int i;
	
	strncpy(retMessage, "Available Commands2:\n\n", bufSize);
	for (i=0; i<sizeof(cmds)/sizeof(cmd_t); i++) {
		strncat(retMessage, cmds[i].ucmd, bufSize);
		strncat(retMessage, ", ", bufSize);
	}
	strncat(retMessage, "\n", bufSize);
	return 0;
}
	
int HandleCommand2(char *message, int messageLen, char *retMessage, int bufSize) {
	int i;
	for (i=0; i<sizeof(cmds)/sizeof(cmd_t); i++) {
		if (strcmp(cmds[i].ucmd, message) == 0) {
			syslog(LOG_DEBUG, "Handling Command2: %s", message);
			if(cmds[i].func != NULL)
				return cmds[i].func(cmds[i].mcmd, retMessage, bufSize);
		}
	}
	syslog(LOG_DEBUG, "Unknown Command2: %s", message);
	return 1;
}

/* jc: replaced by HandleCommand2()
 * 
int HandleCommand(char *message, int messageLen, char *retMessage, int bufSize)
{
  int tmp;
  int len;
  int i;
  time_t rtcTime;
  time_t sysTime;
  struct timeval setTime;
  char timeStr[100];
  struct tm strTime;
  struct tm *strSetTime;
  char buf[15];
  char cmdBuf[15];
  
  syslog(LOG_DEBUG, "Handling Command: %s", message);

  // This is a very ugly list of if-else and strncmp calls...
  
  if(strncmp(message, "DeviceReady", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "DeviceReady");
    if(SendCommand(fd, DeviceReadyCmd, NULL) == SUCCESS)
      strncpy(retMessage, "OK\n", bufSize);
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "GetTemperature", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "GetTemperature");
    if(SendCommand(fd, ThermalStatusGetCmd, buf) > ERR_WRONG_ANSWER)
    {
      tmp = ThermalTable[(int)buf[5]];
      snprintf(retMessage, bufSize, "%d", tmp);
      len = strlen(retMessage);
      if(bufSize > 1)
      {
        retMessage[len] = '\n';
        retMessage[len+1] = '\0';
      }
      write_str_to_file("/tmp/sys/temp1_input", retMessage);
    }
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "DeviceShutdown", strlen("DeviceShutdown")) == 0)
  {
    syslog(LOG_DEBUG, "DeviceShutdown");
    if(messageLen >= (strlen("DeviceShutdown") + 2))
    {
      //tmp = atoi(&message[strlen("DeviceShutdown") + 1]); // FIXME: The parameter is never passed, we default to 10s here..
      //printf("%s\n", tmp);
      if(SendCommand(fd, DeviceShutdownCmd, NULL) == SUCCESS)
        strncpy(retMessage, "OK\n", bufSize);
      else
        strncpy(retMessage, "ERR\n", bufSize);
    }
  }
  
  else if(strncmp(message, "quit", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "Quit");
    strncpy(retMessage, "Bye\n", bufSize);
    return 2;
  }
  
  else if(strncmp(message, "EnablePowerRecovery", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "EnablePowerRecovery");
    if(SendCommand(fd, APREnableCmd, NULL) == SUCCESS)
      strncpy(retMessage, "OK\n", bufSize);
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "DisablePowerRecovery", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "DisablePowerRecovery");
    if(SendCommand(fd, APRDisableCmd, NULL) == SUCCESS)
      strncpy(retMessage, "OK\n", bufSize);
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "GetPowerRecoveryState", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "GetPowerRecoveryState");
    if(SendCommand(fd, APRStatusCmd, buf) > ERR_WRONG_ANSWER)
    {
      snprintf(retMessage, bufSize, "%d", buf[5]);
      len = strlen(retMessage);
      if(bufSize > 1)
      {
        retMessage[len] = '\n';
        retMessage[len+1] = '\0';
      }
    }
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "EnableWOL", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "EnableWOL");
    if(SendCommand(fd, WOLStatusEnableCmd, NULL) == SUCCESS)
      strncpy(retMessage, "OK\n", bufSize);
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "DisableWOL", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "DisableWOL");
    if(SendCommand(fd, WOLStatusDisableCmd, NULL) == SUCCESS)
      strncpy(retMessage, "OK\n", bufSize);
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "GetWOLState", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "GetWOLState");
    if(SendCommand(fd, WOLStatusGetCmd, buf) > ERR_WRONG_ANSWER)
    {
      snprintf(retMessage, bufSize, "%d", buf[5]);
      len = strlen(retMessage);
      if(bufSize > 1)
      {
        retMessage[len] = '\n';
        retMessage[len+1] = '\0';
      }
    }
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "SetFanStop", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "FanStopCmd");
    if(SendCommand(fd, FanStopCmd, NULL) == SUCCESS) {
      strncpy(retMessage, "OK\n", bufSize);
	  fanSpeed = 0;
	  write_str_to_file("/tmp/sys/fan1_input", "0");
	} else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "SetFanHalf", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "FanHalfCmd");
    if(SendCommand(fd, FanHalfCmd, NULL) == SUCCESS) {
      strncpy(retMessage, "OK\n", bufSize);
	  fanSpeed = 1;
	  write_str_to_file("/tmp/sys/fan1_input", "3000");
	} else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "SetFanFull", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "FanFullCmd");
    if(SendCommand(fd, FanFullCmd, NULL) == SUCCESS) {
      strncpy(retMessage, "OK\n", bufSize);
	  fanSpeed = 2;
	  write_str_to_file("/tmp/sys/fan1_input", "6000");
	} else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "PowerLedOn", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "PowerLedOn");
    if(SendCommand(fd, PwrLedOnCmd, NULL) == SUCCESS)
      strncpy(retMessage, "OK\n", bufSize);
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "PowerLedOff", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "PowerLedOff");
    if(SendCommand(fd, PwrLedOffCmd, NULL) == SUCCESS)
      strncpy(retMessage, "OK\n", bufSize);
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "PowerLedBlink", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "PowerLedBlink");
    if(SendCommand(fd, PwrLedBlinkCmd, NULL) == SUCCESS)
      strncpy(retMessage, "OK\n", bufSize);
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "systohc", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "systohc");
    // Copy the command to our buffer
    for(i=0;i<13;i++)
    {
      cmdBuf[i] = WDateAndTimeCmd[i];
    }
    sysTime = time(NULL);
    strSetTime = localtime(&sysTime);
    // Put the current local time into the command buffer
    cmdBuf[5] = (char)strSetTime->tm_sec;
    cmdBuf[6] = (char)strSetTime->tm_min;
    cmdBuf[7] = (char)strSetTime->tm_hour;
    cmdBuf[8] = (char)strSetTime->tm_wday;
    cmdBuf[9] = (char)strSetTime->tm_mday;
    cmdBuf[10] = (char)(strSetTime->tm_mon + 1);
    cmdBuf[11] = (char)(strSetTime->tm_year - 100);
    // And modify the values so that the MCU understands them...
    for(i=5;i<12;i++)
    {
      cmdBuf[i] = ((cmdBuf[i] / 10) << 4) + (cmdBuf[i] % 10);
    }
    if(SendCommand(fd, cmdBuf, NULL) == SUCCESS)
      strncpy(retMessage, "OK\n", bufSize);
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "hctosys", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "hctosys");
    // Retrieve RTC time first
    if(SendCommand(fd, RDateAndTimeCmd, buf) > ERR_WRONG_ANSWER)
    {
      for(i=5;i<12;i++)
      {
        buf[i] = (buf[i] & 0x0f) + 10 * ((buf[i] & 0xf0) >> 4); // The other end is a µC (doh!)
      }

      strTime.tm_year = (100 + (int)buf[11]);
      strTime.tm_mon = buf[10]-1;
      strTime.tm_mday = buf[9];
      strTime.tm_hour = buf[7];
      strTime.tm_min = buf[6];
      strTime.tm_sec = buf[5];
      strTime.tm_isdst = -1;
      rtcTime = mktime(&strTime);
      strcpy(timeStr, ctime(&rtcTime));
      // Retrieve system time
      sysTime = time(NULL);
      setTime.tv_sec = rtcTime;
      setTime.tv_usec = 0;
      // Set the time and print the difference on success
      if(settimeofday(&setTime, NULL) != 0)
        strncpy(retMessage, "ERR\n", bufSize);
      else
        snprintf(retMessage, bufSize, "RTC: %sSys: %sDiff: %.fs\n", timeStr, ctime(&sysTime), difftime(sysTime, rtcTime));
    }
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "ReadRtc", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "ReadRtc");
    if(SendCommand(fd, RDateAndTimeCmd, buf) > ERR_WRONG_ANSWER)
    {
      for(i=5;i<12;i++)
      {
        buf[i] = (buf[i] & 0x0f) + 10 * ((buf[i] & 0xf0) >> 4); // The other end is a µC (doh!)
      }
      strTime.tm_year = (100 + (int)buf[11]);
      strTime.tm_mon = buf[10]-1;
      strTime.tm_mday = buf[9];
      strTime.tm_hour = buf[7];
      strTime.tm_min = buf[6];
      strTime.tm_sec = buf[5];
      strTime.tm_isdst = -1;   
      rtcTime = mktime(&strTime);
      strcpy(timeStr, ctime(&rtcTime));         
      snprintf(retMessage, bufSize, "RTC: %s", timeStr);
    }
    else
    {
      strncpy(retMessage, "ERR\n", bufSize);
      return 1;
    }
  }
  
  else if(strncmp(message, "ShutdownDaemon", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "ShutdownDaemon");
    strncpy(retMessage, "OK\n", bufSize);
    return 3;
  }
  
  else if(strncmp(message, "help", messageLen) == 0)
  {
    syslog(LOG_DEBUG, "help");
    strncpy(retMessage, "Available Commands:\n\n"
			"DeviceReady, DeviceShutdown, ShutdownDaemon,\n"
            "EnablePowerRecovery, DisablePowerRecovery, GetPowerRecoveryState,\n"
            "EnableWOL, DisableWOL, GetWOLState,\n"
			"SetFanStop, SetFanHalf, SetFanFull,\n"
			"PowerLedOn, PowerLedOff, PowerLedBlink,\n"
			"ReadRtc, systohc, hctosys,\n"
			"GetTemperature, quit\n", bufSize);
  }
  else
  {
    strncpy(retMessage, "Command not Understood!\n", bufSize);
  }

  return 0;
}
*/

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
	str[len - 1] = 0;
	return 0;
}

int write_str_to_file(const char *filename, char *str) {
	int fd;

	if ((fd = open(filename, O_WRONLY)) == -1) {
		fd = open(filename, O_WRONLY | O_CREAT, 0644);
		if (fd == -1) {
			syslog(LOG_ERR, "open %s: %m", filename);
			return -1;
		}
	}
	write(fd, str, strlen(str));
	close(fd);
	return 0;
}

int read_int_from_file(const char *filename, int *u) {
	char buf[64];
	if (read_str_from_file(filename, buf, 64))
		return -1;
	*u = atoi(buf);
	return 0;
}

int write_int_to_file(const char *filename, int u) {
	int fd;
	char buf[64];

	fd = open(filename, O_WRONLY);
	if (fd == -1) {
		syslog(LOG_ERR, "open %s: %m", filename);
		return -1;
	}
	sprintf(buf, "%d", u);
	write(fd, buf, strlen(buf));
	close(fd);
	return 0;
}

//jc: end-of copied from sysctrl.c

/*
 * jc: This daemon currently controls the fan speed, but that is 'sysctrl' daemon job.
 * 
 * This daemon should be just an interface between the classical linux interface and the MCU,
 * so, periodicaly:
 * 
 * -read the system temperature from the MCU and write it to /tmp/sys/temp1_input DONE
 * -read /tmp/sys/pwm1 and set the fan speed DONE
 * -update /tmp/sys/fan1_input when the fan speed changes DONE
 * -read /tmp/sys/power_led/trigger and set the power led TODO
 * -read the power button status from the MCU and generate a key input event (see bellow) TODO
 * -use AF_UNIX, providing file based authentication/autorization DONE
 * -...
 * 
 * Don't take the initiative to:
 * -control the fan DONE
 * -powering the box down DONE
 * -do hctosys/systohct DONE
 * -...
 * 
 */

int main(int argc, char *argv[])
{
  char response[500];
  int i;
  pid_t pid;
  pid_t sid;
  int powerBtn;
  int pressed;
  int opt;
  int sleepCount;
  int pollTimeMs;
  char msgBuf[15];
  int temperature;
  int pwm;
  struct sockaddr_un server;
  struct pollfd *fds = NULL;
  nfds_t nfds;
  int retval;
  int ret;
  int msgIdx;
  char message[500];
  pressed = 0;
  nfds = 1;
  opt = 1;
  sleepCount = 0;
  pollTimeMs = 10; // Sleep 10ms for every loop
  
  stDaemonConfig.goDaemon = 1;
  stDaemonConfig.debug = 0;

  // Parse command line arguments
  while((i = getopt(argc, argv, "fd")) != -1)
  {
    switch(i)
    {
      case 'f':
        stDaemonConfig.goDaemon = 0;
        break;
      case 'd':
        stDaemonConfig.debug = 1;
        stDaemonConfig.goDaemon = 0;
        break;
      default:
        fprintf(stderr, "Unknown option character `\\x%x'.\n", optopt);
		fprintf(stderr, "Usage: %s [-f][-d]\n", argv[0]);
        fprintf(stderr, "       where\n");
        fprintf(stderr, "         -f              don't detach\n");
        fprintf(stderr, "         -d              debug (implies -f)\n");
        return EXIT_FAILURE;
    }
  }
  
  // Register some signal handlers
  signal(SIGTERM, sighandler);
  signal(SIGINT, sighandler);
  
  stDaemonConfig.portName = "/dev/ttyS1";
  stDaemonConfig.nRetries = 5;
    
  stDaemonConfig.fanPollTime = 15; 

  stDaemonConfig.gpioDir = "/sys/class/gpio";
  stDaemonConfig.gpioPollTime = 1; 
  stDaemonConfig.pollGpio = 1;
  
  stDaemonConfig.serverName = "/var/run/dns320l.socket"; // using AF_UNIX

  // Setup syslog
  if(stDaemonConfig.debug)
    setlogmask(LOG_UPTO(LOG_DEBUG));
  else
    setlogmask(LOG_UPTO(LOG_INFO));
  
  if(stDaemonConfig.goDaemon)
    openlog("dns320l-daemon", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_LOCAL1);
  else
    openlog("dns320l-daemon", LOG_CONS | LOG_PID | LOG_NDELAY | LOG_PERROR, LOG_LOCAL1);
    
  if(stDaemonConfig.goDaemon)
  {
    pid = fork();
    if(pid < 0)
    {
      syslog(LOG_ERR, "Forking failed.");
      return EXIT_FAILURE;
    }
    
    if(pid > 0)
    {
      return EXIT_SUCCESS;
    }
    // From here on we are the child process...
    umask(0);
    sid = setsid();
    if(sid < 0)
    {
      syslog(LOG_ERR, "Could not create process group");
      return EXIT_FAILURE;
    }
    
    if((chdir("/")) < 0)
    {
       syslog(LOG_ERR, "Could not chdir(\"/\")");
       return EXIT_FAILURE;
    }
    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);
  
  }
  
  // Open our socket server
  if ((ls = socket (AF_UNIX, SOCK_STREAM, 0)) == -1){
    syslog(LOG_ERR, "socket");
    exit(EXIT_FAILURE);
  }

  if (setsockopt(ls,SOL_SOCKET,SO_REUSEADDR,&opt,sizeof opt)<0){
    syslog(LOG_ERR, "setsockopt (SO_RESUSEADDR): %s",strerror(errno));
    exit(EXIT_FAILURE);
  }

  server.sun_family = AF_UNIX;
  strcpy(server.sun_path, stDaemonConfig.serverName);

  syslog(LOG_DEBUG, "Bind name to ls.");
  retval = bind(ls, (struct sockaddr *) &server, sizeof(struct sockaddr_un));
  if (retval)
  {
    syslog(LOG_ERR, "bind");
    cleanup(0, ls,1);
    exit(EXIT_FAILURE);
  }

  syslog(LOG_DEBUG, "Listen on ls for connections.");
  retval = listen (ls, 5);
  if (retval)
  {
    syslog(LOG_ERR, "listen");
    cleanup(0, ls,1);
    exit(EXIT_FAILURE);
  }
  syslog(LOG_INFO, "Server startup success on %s", stDaemonConfig.serverName);

  fds = (struct pollfd *)calloc(1,nfds*sizeof(struct pollfd));
  fds->fd = ls;
  fds->events = POLLIN | POLLPRI;

  fd = open (stDaemonConfig.portName, O_RDWR | O_NOCTTY | O_SYNC);
  if (fd < 0)
  {
    syslog(LOG_ERR, "error %d opening %s: %s", errno, stDaemonConfig.portName, strerror (errno));
    return EXIT_FAILURE;  
  }

  set_interface_attribs (fd, B115200, 0);  // set speed to 115,200 bps, 8n1 (no parity)
  set_blocking (fd, 0);                // set no blocking

  // Send the DeviceReady command to the MCU
  if(SendCommand(fd, DeviceReadyCmd, NULL) == SUCCESS)
    syslog(LOG_INFO, "dns320l-daemon startup complete, going to FanControl mode");
  else
  {
    syslog(LOG_ERR, "Error sending DeviceReady command.");
//jc: FIXME return EXIT_FAILURE;
  }
  
  // Go to endless loop and do the following:
  // Get the thermal status
  // get desired fan speed and set it
  // Wake every 1s to poll the power button GPIO
  // Wake every few ms to poll the sockets for connections
  // Sleep
  
  while(1)
  {
    sleepCount = 0;
	
    if(SendCommand(fd, ThermalStatusGetCmd, msgBuf) > ERR_WRONG_ANSWER)
      temperature = msgBuf[5];
	else
      temperature = 0;
	
    if(temperature > 0) {
      temperature = ThermalTable[temperature];
	  write_int_to_file("/tmp/sys/temp1_input", temperature);
      syslog(LOG_DEBUG, "Read Temperature: %i", temperature);  
	} else {
      syslog(LOG_ERR, "Error reading Temperature!");
    }

	if (read_int_from_file("/tmp/sys/pwm1", &pwm)) {
		syslog(LOG_ERR, "Error reading pwm1!");
	} else {
		if (pwm == 0 && fanSpeed != 0) {
			SendCommand(fd, FanStopCmd, NULL);
			write_str_to_file("/tmp/sys/fan1_input", "0");
			fanSpeed = 0;
		} else if (pwm < 128 && fanSpeed != 1) {
			SendCommand(fd, FanHalfCmd, NULL);
			write_str_to_file("/tmp/sys/fan1_input", "3000");
			fanSpeed = 1;
		} else if (fanSpeed != 2) {
			SendCommand(fd, FanFullCmd, NULL);
			write_str_to_file("/tmp/sys/fan1_input", "6000");
			fanSpeed = 2;
		}
	}

    while((sleepCount  * pollTimeMs) < (stDaemonConfig.fanPollTime * 1000))
    {
      if(stDaemonConfig.pollGpio && (((sleepCount * pollTimeMs) % (stDaemonConfig.gpioPollTime* 1000)) == 0))
      {
        if(gpio_get_value(GPIO_BUTTON_POWER, &powerBtn) == 0)
        {

/*
 * jc: FIXME: configure and compile the kernel uinput driver (drivers/input/misc, 10KB) and inject the event
 * https://web.archive.org/web/20120710121647/http://www.einfochips.com/download/dash_jan_tip.pdf
 * https://media.readthedocs.org/pdf/python-evdev/latest/python-evdev.pdf
 * Those injected events will appear under /dev/event1. How to redirect them to /dev/event0?
 * 
 * could it be that the GPIO where the power button is connected is not able to generate interrupts?
 * Are interrupts needed to generate events? There is a kernel configure option to use on GPIOs that are
 * not able to generate interrupst. Try that first, instead of the uinput driver?
 */
          if((powerBtn == 0) && !pressed)
          {
            pressed = 1;
            syslog(LOG_INFO, "Power Button Pressed!");
			// If DeviceReady is sent instead of DeviceShutdown, will the MCU recover and continue?
            //SendCommand(fd, DeviceShutdownCmd, NULL);
            execl("/sbin/poweroff", "poweroff", (char *)0);
          }
        }

      }
      sleepCount++;

      ret=poll(fds,nfds,pollTimeMs); // Time out after pollTimeMs
      if (ret == -1){
        syslog(LOG_ERR, "poll");
        exit(EXIT_FAILURE);
      }
      for (i=0;(i<nfds) && (ret);i++)
      {
        if (!(fds+i)->revents)
          continue;
        ret--;
        if (((fds+i)->fd == ls) && ((fds+i)->revents & POLLIN))
        {
          /*
                     * Accept connection from socket ls:
                     * accepted connection will be on socket (fds+nfds)->fd.
                     */
          syslog(LOG_DEBUG, "POLLIN on ls. Accepting connection");
//          namelength = sizeof (s_name);
          fds = (struct pollfd *)realloc(fds,(nfds+1)*sizeof(struct pollfd));
//          (fds+nfds)->fd  = accept (ls, (struct sockaddr *)&s_name, &namelength);
		  (fds+nfds)->fd  = accept (ls, NULL, 0);
          if ((fds+nfds)->fd == -1)
          {
            syslog(LOG_ERR, "accept");
            cleanup(0, (fds+nfds)->fd, 1);
            fds = (struct pollfd *)realloc(fds,nfds*sizeof(struct pollfd));
            continue;
          }
          (fds+nfds)->events = POLLIN | POLLRDNORM;
          nfds++;
          continue;
        }
        if ((fds+i)->revents & POLLNVAL)
        {
          syslog(LOG_DEBUG, "POLLNVAL on socket. Freeing resource");
          nfds--;
          memcpy(fds+i,fds+i+1,nfds-i);
          fds = (struct pollfd *)realloc(fds,nfds*sizeof(struct pollfd));
          continue;
        }
        if ((fds+i)->revents & POLLHUP)
        {
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
        if ((fds+i)->revents & POLLRDNORM)
        {
          retval = recv((fds+i)->fd, message, sizeof(message)-1, 0); // Don't forget the string terminator here!
          syslog(LOG_DEBUG, "-> (recv) retval = %d.",retval);  /* ped */
          msgIdx = retval;
          if (retval <=0)
          {
            if (retval == 0)
            {
              syslog(LOG_DEBUG, "recv()==0 => peer disconnected...");
              cleanup(1,(fds+i)->fd,2);
            }
            else
            {
              syslog(LOG_ERR, "receive");
              cleanup( 0, (fds+i)->fd,1);
            }
            nfds--;
            memcpy(fds+i,fds+i+1,nfds-i);
            fds = (struct pollfd *)realloc(fds,nfds*sizeof(struct pollfd));
            continue;
          }
/* jc : FIXME: assumes <CR><LF> as EOL. some telnet clients migh send only <LF>.
 'telnet> toggle crlf' Will send carriage return as <CR><LF>.
 From the shell, use 'echo -e 'foobar\r | nc local:/var/run/dns320l.socket'
*/
          while((retval > 0) && (message[msgIdx-2] != '\r') && ((msgIdx+1) < sizeof(message)))
          {
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

          //syslog(LOG_DEBUG, "Normal message :  %.*s\n",retval,message);
		  msgIdx = HandleCommand2(message, msgIdx, response, sizeof(response));
          retval = send((fds+i)->fd, response, strlen(response), 0);
          if((retval < 0) || (msgIdx > 1))
          {
            syslog(LOG_DEBUG, "send()==0 => peer disconnected...");
            cleanup(1,(fds+1)->fd, 2);
          }
          if(msgIdx == 3)
          {
            syslog(LOG_INFO, "Shutting down dns320l-daemon...");
			unlink(stDaemonConfig.serverName);
            return EXIT_SUCCESS;
          }
          continue;
        }
      }
    }
  }
  closelog();
  return EXIT_SUCCESS;
}
