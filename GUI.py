import wx
import os

def OnEraseBack(self,event):
    dc = event.GetDC()
    if not dc:
        dc = wx.ClientDC(self)
        rect = self.GetUpdateRegion().GetBox()
        dc.SetClippingRect(rect)
    dc.Clear()
    bmp = wx.Bitmap('D:\\PythonProject\\12.jpg')
    dc.DrawBitmap(bmp, 0, 0)

def train(event):
    os.system('python Face_train.py')

def faceCatch(event):
    os.system('python Face_Catch.py')

def Login(event):
    os.system('python Log.py')
    Catch_button = wx.Button(frame,style=1,label="开始录入", pos=(150, 190), size=(180, 40))
    Catch_button.Bind(wx.EVT_BUTTON, faceCatch)
    Train_button = wx.Button(frame,style=1,label="保存模型", pos=(150, 240), size=(180, 40))
    Train_button.Bind(wx.EVT_BUTTON, train)

def faceRecognition(event):
    os.system('python Face_recognition.py')

app = wx.App()
frame = wx.Frame(None, title="Face recognition attendance system", pos=(1000, 200), size=(500, 400),
                 style = wx.DEFAULT_FRAME_STYLE)
panel = wx.Panel()
panel.Bind(wx.EVT_ERASE_BACKGROUND,OnEraseBack)

text = wx.StaticText(frame, -1,'基于人脸识别医院考勤系统',(160,80))
font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, 'Consolas')
text.SetFont(font1)


# 录入按钮创建
open_button = wx.Button(frame,style=1,label="录入新的用户", pos=(130, 130), size=(100, 50))
open_button.Bind(wx.EVT_BUTTON, Login)

# 识别按钮创建
open_button = wx.Button(frame, label="签到", pos=(250, 130), size=(100, 50))
open_button.Bind(wx.EVT_BUTTON, faceRecognition)


frame.Show()
app.MainLoop()