#ifndef DNS320L_DAEMON_H
#define DNS320L_DAEMON_H


typedef struct {
  int goDaemon;
  int xcmd;
  int debug;
  char *serverName;
  char *portName;
  int nRetries;
} DaemonConfig;

int simple_cmd(char *mcmd, char *retMessage, int bufSize);
int simple_cmd2(char *mcmd, char *retMessage, int bufSize);
int setpowerled_cmd(char *mcmd, char *retMessage, int bufSize);
int setfan_cmd(char *mcmd, char *retMessage, int bufSize);
int readrtc_cmd(char *mcmd, char *retMessage, int bufSize);
int systohc_cmd(char *mcmd, char *retMessage, int bufSize);
int hctosys_cmd(char *mcmd, char *retMessage, int bufSize);
int gettemperature_cmd(char *mcmd, char *retMessage, int bufSize);
int help_cmd(char *mcmd, char *retMessage, int bufSize);
int quit_cmd(char *mcmd, char *retMessage, int bufSize);
int shutdowndaemon_cmd(char *mcmd, char *retMessage, int bufSize);

typedef struct {
	char *ucmd;
	char *mcmd;
	int  (*func)(char *, char *, int);
} cmd_t ;

cmd_t cmds[] = {
	{"DeviceReady", DeviceReadyCmd, simple_cmd},
	{"DeviceShutdown", DeviceShutdownCmd, simple_cmd},
	{"ShutdownDaemon", NULL, shutdowndaemon_cmd},
	{"EnablePowerRecovery", APREnableCmd, simple_cmd},
	{"DisablePowerRecovery", APRDisableCmd, simple_cmd},
	{"GetPowerRecoveryState", APRStatusCmd, simple_cmd2},
	{"EnableWOL", WOLStatusEnableCmd, simple_cmd},
	{"DisableWOL", WOLStatusDisableCmd, simple_cmd},
	{"GetWOLState", WOLStatusGetCmd, simple_cmd2},
	{"SetFanStop", FanStopCmd, setfan_cmd},
	{"SetFanHalf", FanHalfCmd, setfan_cmd},
	{"SetFanFull", FanFullCmd, setfan_cmd},
	{"PowerLedOn", PwrLedOnCmd, setpowerled_cmd},
	{"PowerLedOff", PwrLedOffCmd, setpowerled_cmd},
	{"PowerLedBlink", PwrLedBlinkCmd, setpowerled_cmd},
	{"ReadRtc", RDateAndTimeCmd, readrtc_cmd},
	{"systohc", WDateAndTimeCmd, systohc_cmd},
	{"hctosys", RDateAndTimeCmd, hctosys_cmd},
	{"GetTemperature", ThermalStatusGetCmd, gettemperature_cmd},
	{"help", NULL, help_cmd},
	{"quit", NULL, quit_cmd},
};

/** <i>Function</i> that reads a GPIO value from sysfs interface.
  @param gpio The GPIO number to read
  @param value Pointer where the value is to be put
  @param gpioDir Pointer containing the sysfs path to the GPIO subdir
  @return The GPIO's value
  */
int gpio_get_value(unsigned int gpio, unsigned int *value);

/** <i>Function</i> that cleans up a socket after shutdown
  @param shut If 1, the socket is shutdown first
  @param s The socket to work on
  @param howmany Number of sockets to close?
*/
void cleanup(int shut,int s,int howmany);

/** <i>Function</i> that is called by the OS upon sending a signal
    to the application
 @param sig The signal number received
*/
static void quithandler(int sig);

/** <i>Function</i> that sets interface attributes on a given
  serial port.
 @param fd The file descriptor (serial port) to work with
 @param speed The speed the interface to configure
 @param parity Use parity or not
 @return 0 on success, otherwise 1
*/
int set_interface_attribs (int fd, int speed, int parity);

/** <i>Function</i> that sets an interface to either blocking
  or non-blocking mode
  @param fd The file descriptor to work with
  @param should_block Flag whether it should block or not
*/
void set_blocking (int fd, int should_block);

/** <i>Function</i> that checks the first few bytes of the MCU's response
  whether it corresponds to the sent command
  @param buf The buffer to compare
  @param cmd The command that was sent
  @param len The lenght of the command
  @return SUCCESS on success, otherwise ERR_WRONG_ANSWER
*/
int CheckResponse(char *buf, char *cmd, int len);

/** <i>Function</i> that clears the current Serial Port buffer
 by reading some bytes
 @param fd The serial port to work on
 */
void ClearSerialPort(int fd);

/** <i>Function</i> that wraps around the internal send command and handles retry
  @param fd The serial port to work on
  @param cmd The command to send
  @param outArray An array where the response shall be put, can be NULL for no response
  @return SUCCESS, ERR_WRONG_ANSWER or the number of bytes received
  */
int SendCommand(int fd, char *cmd, char *outArray);

/** <i>Function</i> that sends a command to the MCU and waits
  for response and/or ACK.
  @param fd The serial port to work on
  @param cmd The command to send
  @param outArray An array where the response shall be put, can be NULL for no response
  @return SUCCESS, ERR_WRONG_ANSWER or the number of bytes received
  */
int _SendCommand(int fd, char *cmd, char *outArray);

/** <i>Function</i> that handles commands received by the socket
  and puts the response back into the retMessage buffer
  @param message The message that was received (the command)
  @param messageLen The lenght of the received message
  @param retMessage Pointer to an output array for the response message
  @parma bufSize The size of the message buffer
  @return 0 on success, 1 on failure, 2 for quit and 3 for daemon shutdown
*/
int HandleCommand(char *message, int messageLen, char *retMessage, int bufSize);
int HandleCommand2(char *message, int messageLen, char *retMessage, int bufSize);

/** <i>Main Function</i>
  @param argc The argument count
  @param argv The argument vector
  @return EXIT_SUCCESS on success, otherwise EXIT_ERROR
*/
int main(int argc, char *argv[]);

int read_str_from_file(const char *filename, char *str, int sz);
int write_str_to_file(const char *filename, char *str);
int read_int_from_file(const char *filename, int *u);
int write_int_to_file(const char *filename, int u);

#endif //DNS320L_DAEMON_H
