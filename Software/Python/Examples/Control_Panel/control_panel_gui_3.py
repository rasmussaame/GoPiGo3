#!/usr/bin/python

from __future__ import print_function
import subprocess

# try to import the auto_detection library
try:
    import auto_detect_robot
    no_auto_detect = False
except:
    no_auto_detect = True

try:
    import wx
except ImportError:
    raise ImportError("The wxPython module is required to run this program")

import easygopigo3 as easy
try:
    gpg = easy.EasyGoPiGo3()
except Exception as e:
    print("GoPiGo3 cannot be instanstiated. Most likely wrong firmware version")
    print(e)
    app = wx.App()
    wx.MessageBox('GoPiGo3 cannot be found. It may need a firmware update.\n\nYou can upgrade the firmware by running DI Software Update then updating your robot.', 'GoPiGo3 not found', wx.OK | wx.ICON_ERROR)
    exit()

import atexit
atexit.register(gpg.stop)
process = None

left_led=0
right_led=0
left_eye=0
right_eye=0
v=gpg.volt()


firmware_version=gpg.get_version_firmware()
try:
    library_version=easy.__version__
except:
    library_version=""

ticks = gpg.ENCODER_TICKS_PER_ROTATION
serial = gpg.get_id()

ICON_PATH = "/home/pi/Dexter/GoPiGo3/Software/Python/Examples/Control_Panel/"


class MainPanel(wx.Panel):
    """"""
    #----------------------------------------------------------------------
    def __init__(self, parent):

        wx.Panel.__init__(self, parent=parent)
        #self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.WHITE)
        self.frame = parent


        title_font = wx.Font( 15,
                        wx.FONTFAMILY_DEFAULT,
                        wx.FONTSTYLE_NORMAL,
                        wx.FONTWEIGHT_BOLD)
        title_font.SetUnderlined(False)

        small_font = wx.Font( 10,
                        wx.FONTFAMILY_DEFAULT,
                        wx.FONTSTYLE_NORMAL,
                        wx.FONTWEIGHT_BOLD)
        small_font.SetUnderlined(False)

        # main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        # Two horizontal sections
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # top has two horizontal sections
        control_sizer = wx.BoxSizer(wx.VERTICAL)
        vital_signs_sizer = wx.BoxSizer(wx.VERTICAL)


        if no_auto_detect == True:
            detected_robot = auto_detect_robot.autodetect()
            print(detected_robot)
            if detected_robot != "GoPiGo3":
                detected_robot_str = wx.StaticText(self,-1,
                    label="Warning: Could not find a GoPiGo3")
                detected_robot_str.SetForegroundColour('red')
                warning_sizer = wx.BoxSizer(wx.HORIZONTAL)
                warning_sizer.Add(detected_robot_str, 0, wx.EXPAND| wx.ALIGN_CENTER)
                main_sizer.Add(warning_sizer, 0, wx.ALIGN_CENTER)


        # Remote Control
        control_label = wx.StaticText(self, -1, label="Remote Control:")
        control_label.SetFont(title_font)

        left_led_button = wx.Button(self, label="Left Blinker")
        self.Bind(wx.EVT_BUTTON, self.left_led_button_OnButtonClick, left_led_button)
        right_led_button = wx.Button(self, label="Right Blinker")
        self.Bind(wx.EVT_BUTTON, self.right_led_button_OnButtonClick, right_led_button)

        led_sizer = wx.BoxSizer(wx.HORIZONTAL)
        led_sizer.Add(left_led_button, 0, wx.TOP,9)
        led_sizer.AddSpacer(130)
        led_sizer.Add(right_led_button, 0, wx.TOP,9)

        eyes_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_eye_button = wx.Button(self, label="Left Eye ")
        self.Bind(wx.EVT_BUTTON, self.left_eye_button_OnButtonClick, left_eye_button)
        bmp = wx.Bitmap(ICON_PATH+"dex.png",type=wx.BITMAP_TYPE_PNG)
        robotbitmap=wx.StaticBitmap(self, bitmap=bmp)
        right_eye_button = wx.Button(self, label="Right Eye")
        self.Bind(wx.EVT_BUTTON, self.right_eye_button_OnButtonClick, right_eye_button)

        eyes_sizer.Add(right_eye_button, 0, wx.ALIGN_CENTER)
        eyes_sizer.Add(robotbitmap, 0, wx.ALIGN_CENTER)
        eyes_sizer.Add(left_eye_button, 0, wx.ALIGN_CENTER)

        fwd_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fwd_button = wx.Button(self, label="Forward")
        self.Bind(wx.EVT_BUTTON, self.fwd_button_OnButtonClick, fwd_button)
        fwd_sizer.Add(fwd_button, 0, wx.ALIGN_CENTER)

        middle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_button = wx.Button(self, label="Left")
        self.Bind(wx.EVT_BUTTON, self.left_button_OnButtonClick, left_button)
        stop_button = wx.Button(self, label="Stop")
        stop_button.SetForegroundColour('red')
        self.Bind(wx.EVT_BUTTON, self.stop_button_OnButtonClick, stop_button)
        right_button = wx.Button(self, label="Right")
        self.Bind(wx.EVT_BUTTON, self.right_button_OnButtonClick, right_button)

        middle_sizer.Add(left_button, 0, wx.ALIGN_CENTER)
        middle_sizer.Add(stop_button,  0, wx.ALIGN_CENTER)
        middle_sizer.Add(right_button,  0, wx.ALIGN_CENTER)

        bwd_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bwd_button = wx.Button(self, label="Back")
        self.Bind(wx.EVT_BUTTON, self.bwd_button_OnButtonClick, bwd_button)
        bwd_sizer.Add(bwd_button,  0, wx.ALIGN_CENTER)

        # Vital Signs Values

        vital_signs_label = wx.StaticText(self, -1, label="Vital Signs:")
        vital_signs_label.SetFont(title_font)

        batterySizer = wx.BoxSizer(wx.HORIZONTAL)
        battery_button = wx.Button(self, label="Check Battery Voltage")
        self.Bind(wx.EVT_BUTTON, self.battery_button_OnButtonClick, battery_button)
        self.battery_label = wx.StaticText(self, label=str(round(v,1))+"V")
        batterySizer.Add(battery_button, 0, wx.ALIGN_LEFT )
        batterySizer.AddSpacer(22)
        batterySizer.Add( self.battery_label,0, wx.EXPAND )

        firmwareSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.firmware_label = wx.StaticText(self,-1,label="Firmware Version: "+str(firmware_version))
        firmwareSizer.Add( self.firmware_label, 0, wx.EXPAND )

        SerialNoSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.serial_label = wx.StaticText(self,-1,label="Serial Number: "+str(serial))
        SerialNoSizer.Add( self.serial_label, 0, wx.EXPAND )

        tickSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ticks_label = wx.StaticText(self,-1,label="Ticks per Motor: "+str(ticks))
        tickSizer.Add( self.ticks_label, 0, wx.EXPAND )

        versionSizer = wx.BoxSizer(wx.HORIZONTAL)
        print(library_version)
        if library_version != "":
            self.version_label = wx.StaticText(self,-1,label="Driver Version: "+str(library_version))
            versionSizer.Add( self.version_label, 0, wx.EXPAND )

        # Exit
        exit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        exit_button = wx.Button(self, label="Exit")
        exit_button.Bind(wx.EVT_BUTTON, self.onClose)
        self.msg_label = wx.StaticText(self, -1, size=(400,30), label="")
        exit_sizer.Add(self.msg_label, 1, wx.ALIGN_LEFT|wx.EXPAND)
        exit_sizer.Add(exit_button, 0, wx.RIGHT, 20)

        # Fill remote control section
        control_sizer.Add(control_label, 0, wx.ALIGN_CENTER|wx.BOTTOM,10)
        control_sizer.Add(led_sizer, 0, wx.ALIGN_CENTER)
        control_sizer.Add(eyes_sizer, 0, wx.ALIGN_CENTER)
        control_sizer.Add(fwd_sizer, 0, wx.ALIGN_CENTER|wx.TOP,10)
        control_sizer.Add(middle_sizer, 0, wx.ALIGN_CENTER)
        control_sizer.Add(bwd_sizer, 0, wx.ALIGN_CENTER)

        vital_extra_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Fill check buttons
        vital_signs_sizer.Add(vital_signs_label, 0, wx.ALIGN_LEFT|wx.BOTTOM, 10)
        vital_signs_sizer.Add(batterySizer, 0, wx.ALIGN_LEFT|wx.TOP,9)
        vital_signs_sizer.Add(firmwareSizer, 0, wx.ALIGN_LEFT|wx.TOP,10)
        vital_signs_sizer.Add(SerialNoSizer, 0, wx.ALIGN_LEFT|wx.TOP,10)
        vital_signs_sizer.Add(tickSizer, 0, wx.ALIGN_LEFT|wx.TOP,10)
        vital_signs_sizer.Add(versionSizer, 0, wx.ALIGN_LEFT|wx.TOP,10)

        drive_forward_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.drive_forward_input_field = wx.TextCtrl(self, -1, "", (0, 0), (50, 30))
        confirm_drive_forward = wx.Button(self, label="Straight (cm)")
        confirm_drive_forward.Bind(wx.EVT_BUTTON, self.drive_forward_cm)
        drive_forward_sizer.Add(self.drive_forward_input_field, 0, wx.LEFT|wx.TOP, 0, 0)
        drive_forward_sizer.Add(confirm_drive_forward, 0, wx.LEFT, 10, 0)

        turn_deg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.turn_deg_input_field = wx.TextCtrl(self, -1, "", (0, 0), (50, 30))
        confirm_turn_deg = wx.Button(self, label="Turn (deg)")
        confirm_turn_deg.Bind(wx.EVT_BUTTON, self.turn_degrees)
        turn_deg_sizer.Add(self.turn_deg_input_field, 0, wx.LEFT|wx.TOP, 0, 0)
        turn_deg_sizer.Add(confirm_turn_deg, 0, wx.LEFT, 10, 0)



        robo1_sizer = wx.BoxSizer(wx.VERTICAL)
        robo1_sizer.Add(drive_forward_sizer, 0, wx.LEFT|wx.TOP, 0, 0)
        robo1_sizer.Add(turn_deg_sizer, 0, wx.LEFT|wx.TOP, 0, 0)

        vital_extra_sizer.Add(vital_signs_sizer, 0, wx.LEFT|wx.TOP, 30, 40)
        vital_extra_sizer.Add(robo1_sizer, 0, wx.LEFT|wx.TOP, 30, 40)
        main_sizer.Add(control_sizer, 0, wx.LEFT|wx.TOP, 30, 20)
        main_sizer.Add(vital_extra_sizer, 0, wx.LEFT|wx.TOP, 0, 0)

        # main_sizer.Add(top_sizer, 0, wx.LEFT|wx.TOP, 30)
        main_sizer.Add(bottom_sizer, 0, wx.LEFT|wx.TOP, 30)
        main_sizer.Add(exit_sizer, 1, wx.ALIGN_RIGHT|wx.TOP|wx.RIGHT, 10)

        self.SetSizerAndFit(main_sizer)

    def battery_button_OnButtonClick(self,event):
        global v
        v=round(gpg.volt(),1)
        self.battery_label.SetLabel(str(v)+"V")

    def firmware_button_OnButtonClick(self,event):
        global firmware_version
        firmware_version=gpg.get_version_firmware()
        self.firmware_label.SetLabel(str(firmware_version))

    def left_button_OnButtonClick(self,event):
        gpg.left()

    def stop_button_OnButtonClick(self,event):
        if process:
            process.terminate()
        gpg.stop()

    def right_button_OnButtonClick(self,event):
        gpg.right()

    def fwd_button_OnButtonClick(self,event):
        gpg.forward()

    def bwd_button_OnButtonClick(self,event):
        gpg.backward()

    def left_led_button_OnButtonClick(self,event):
        global left_led
        if left_led==0:
            gpg.led_on(1)
            left_led=1
        else :
            gpg.led_off(1)
            left_led=0

    def right_led_button_OnButtonClick(self,event):
        global right_led
        if right_led==0:
            gpg.led_on(0)
            right_led=1
        else :
            gpg.led_off(0)
            right_led=0

    def right_eye_button_OnButtonClick(self,event):
        global right_eye
        if right_eye==0:
            gpg.open_right_eye()
            right_eye=1
        else :
            gpg.close_right_eye()
            right_eye=0

    def left_eye_button_OnButtonClick(self,event):
        global left_eye
        if left_eye==0:
            gpg.open_left_eye()
            left_eye=1
        else :
            gpg.close_left_eye()
            left_eye=0


    def drive_forward_cm(self, event):
        try:
            cm = int(self.drive_forward_input_field.GetLineText(0))
            gpg.drive_cm(cm, False)
            self.msg_label.SetLabel("")  # Could maybe use this, the problem is, that is seems to change shape when executed
        except:
            self.msg_label.SetLabel("Straight command input has to be an integer")  # Same as other SetLabel


    def turn_degrees(self, event):
        try:
            deg = int(self.turn_deg_input_field.GetLineText(0))
            gpg.turn_degrees(deg)
            self.msg_label.SetLabel("")  # Could maybe use this, the problem is, that is seems to change shape when executed
        except:
            self.msg_label.SetLabel("Turn command input has to be an integer")

 
    def onClose(self, event):	# Close the entire program.
        self.frame.Close()

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Log.SetVerbose(False)
        wx.Frame.__init__(self, None, title='GoPiGo3 Control Panel', size=(440,640))
        panel = MainPanel(self)
        self.Center()

class Main(wx.App):
    def __init__(self, redirect=False, filename=None):
        """Constructor"""
        wx.App.__init__(self, redirect, filename)
        dlg = MainFrame()
        dlg.Show()

if __name__ == "__main__":
    app = Main()
    app.MainLoop()
