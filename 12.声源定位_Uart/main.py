from Maix import MIC_ARRAY as mic
import lcd,time
import math
from machine import UART, Timer
from fpioa_manager import fm
import utime


#<-----------------用户变量----------------->#
uart = 0 # 串口
Sound_Information = [0]*4 # 声源信息: 0-Y坐标，1-x坐标，2-声音强度，3-角度

X_Coordinate = 0          # 声源x坐标
Y_Coordinate = 0          # 声源y坐标
Sound_Intensity = 0       # 声源强度
Sound_Angle = 0           # 声源角度

Filtering_Flag = 0        # 滤波标志
Sound_Filtering = [0]*4   # 滤波后的声源信息(0-Y坐标，1-x坐标，2-声音强度，3-角度)

#<-----------------初始化配置函数----------------->#
def Config_Init():
  global uart
  mic.init()#可自定义配置 IO
  # 映射串口引脚
  fm.register(6, fm.fpioa.UART1_RX, force=True)
  fm.register(7, fm.fpioa.UART1_TX, force=True)
  uart = UART(UART.UART1, 115200, read_buf_len=4096) # 初始化串口

#<-----------------获取声源信息函数----------------->#
def Get_Mic_Dir():
  AngleX = 0
  AngleY = 0
  AngleR = 0
  Angle = 0
  AngleAddPi = 0

  mic_list = [0]*4
  imga = mic.get_map()    # 获取声音源分布图像
  b = mic.get_dir(imga)   # 计算、获取声源方向

  for i in range(len(b)):
      if (b[i] >= 2):
          AngleX += b[i] * math.sin(i * math.pi/6)
          AngleY += b[i] * math.cos(i * math.pi/6)

  AngleX = round(AngleX, 6) #计算坐标转换值
  AngleY = round(AngleY, 6)

  if (AngleY < 0):
    AngleAddPi = 180
  if (AngleX < 0 and AngleY > 0):
    AngleAddPi = 360
  if (AngleX != 0) or (AngleY != 0): # 参数修正
      if (AngleY == 0):
          Angle = 90 if AngleX > 0 else 270 # 填补X轴角度
      else:
          Angle = AngleAddPi + round(math.degrees(math.atan(AngleX/AngleY)), 4) # 计算角度

      AngleR = round(math.sqrt(AngleY*AngleY+AngleX*AngleX), 4) #计算强度
      mic_list[1] = AngleX
      mic_list[0] = AngleY
      mic_list[2] = AngleR
      mic_list[3] = Angle
  a = mic.set_led(b, (84, 215, 109))# 配置 RGB LED 颜色值

  return mic_list #返回列表，Y坐标，X坐标，强度，角度

#<-----------------调用初始化配置----------------->#
Config_Init()

#<-----------------while循环----------------->#
while True:
  Angle_Str = 0
  Sound_Information = Get_Mic_Dir() # 获取声源参数

  if (Sound_Information[2] >= 17): # 过滤响度较小杂音
    if (Filtering_Flag <= 8): # 均值滤波次数
      Filtering_Flag += 1
      #print(Filtering_Flag)
      X_Coordinate += Sound_Information[1]
      Y_Coordinate += Sound_Information[0]
      Sound_Intensity += Sound_Information[2]
      Sound_Angle += Sound_Information[3]
    elif (Filtering_Flag >= 9):
      Sound_Filtering[1] = X_Coordinate/10
      Sound_Filtering[0] = Y_Coordinate/10
      Sound_Filtering[2] = Sound_Intensity/10
      Sound_Filtering[3] = Sound_Angle/10

      #print(Sound_Filtering) # 打印滤波值
      Angle_Str = '%.0f' % Sound_Filtering[3]
      str1 = '(' + Angle_Str + ')'
      print(str1)
      uart.write(str1)  # 将滤波值通过串口发送

      Filtering_Flag = 0
      X_Coordinate = 0
      Y_Coordinate = 0
      Sound_Intensity = 0
      Sound_Angle = 0

      Sound_Filtering[1] = 0
      Sound_Filtering[0] = 0
      Sound_Filtering[2] = 0
      Sound_Filtering[3] = 0

  #time.sleep_ms(100)
