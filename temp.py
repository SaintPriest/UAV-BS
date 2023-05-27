# # https://hackmd.io/@yizhewang/H1Uyq-Q4m
# from vpython import *
#
# """
#  1. 參數設定, 設定變數及初始值
# """
# size = 10  # 木塊邊長
# L = 200  # 地板長度
# t = 0  # 時間
# dt = 0.01  # 時間間隔
# re = False  # 重置狀態
# running = False  # 物體運動狀態
# end = False  # 程式是否結束
#
# """
#  2. 畫面及函式設定
# """
# # 初始畫面設定
# scene = canvas(title="1D Motion\n\n", width=800, height=400, x=0, y=0,
#                center=vec(0, 5, 0), background=vec(0, 0.6, 0.6))
# scene.caption = "\n"
# floor = box(pos=vec(0, 0, 0), size=vec(L, 0.1 * size, 0.5 * L), color=color.blue)
# cube = box(pos=vec(0, 0.55 * size, 0), size=vec(size, size, size), v=vec(0, 0, 0), color=color.red)
# proj = cone(pos=vec(0, 0, 0), axis=vec(0, 64, 0), radius=16, opacity=0.5)
# gd = graph(title="<i>x</i>-<i>t</i> plot", width=600, height=450, x=0, y=400,
#            xtitle="<i>t</i> (s)", ytitle="<i>x</i> (cm)", fast=False)
# gd2 = graph(title="<i>v</i>-<i>t</i> plot", width=600, height=450, x=0, y=850,
#             xtitle="<i>t</i> (s)", ytitle="<i>v</i> (c  m/s)", ymin=-6.0, ymax=6.0, fast=False)
#
# xt = gcurve(graph=gd, color=color.red)
# vt = gcurve(graph=gd2, color=color.red)
#
#
# # 執行按鈕
# def run(b1):
#      global running
#      running = not running
#      if running:
#           b1.text = "Pause"
#      else:
#           b1.text = "Run"
#
#
# b1 = button(text="Run", pos=scene.title_anchor, bind=run)
#
#
# # 重置按鈕
# def reset(b2):
#      global re
#      re = not re
#
#
# b2 = button(text="Reset", pos=scene.title_anchor, bind=reset)
#
#
# # 重置用, 初始化
# def init():
#      global re, running
#      cube.pos = vec(0, size * 0.55, 0)
#      cube.v.x = vslider.value
#      proj.v.x = vslider.value
#      t = 0
#      xt.delete()
#      vt.delete()
#      re = False
#      running = False
#      b1.text = "Run"
#
#
# # 停止按鈕
# def stop(b3):
#      global end
#      end = not end
# b3 = button(text="Stop Program", pos=scene.title_anchor, bind=stop)
#
# def setTopView(b):
#     scene.camera.pos = vec(0, 135, 0)
#     scene.camera.axis = vec(0, -135, 0)
#     scene.autoscale = True
#     scene.userzoom = True
#     scene.userspin = True
#     scene.userpan = True
#
# b4 = button(text="Top View", pos=scene.title_anchor, bind=setTopView)
#
# # 設定速度滑桿
# def setv(vslider):
#      cube.v.x = vslider.value
#      proj.v.x = vslider.value
#      vtext.text = '{:1.1f} cm/s'.format(vslider.value)
#
#
# vslider = slider(min=-5.0, max=5.0, value=1.0, length=200, bind=setv, right=15,
#                  pos=scene.title_anchor)
# vtext = wtext(text='{:1.1f} cm/s'.format(vslider.value), pos=scene.title_anchor)
# cube.v.x = vslider.value
#
#
# # 更新狀態
# def update():
#      global t
#      rate(1000)
#      cube.pos += cube.v * dt
#      proj.pos += cube.v * dt
#      xt.plot(pos=(t, cube.pos.x))
#      vt.plot(pos=(t, cube.v.x))
#      t += dt
#      print(scene.camera.pos)
#      print(scene.camera.axis)
#
#
# """
#  3. 主程式
# """
# while not end:
#      if (cube.pos.x <= -L * 0.5 + size * 0.5 and cube.v.x < 0) or (
#              cube.pos.x >= L * 0.5 - size * 0.5 and cube.v.x > 0): cube.v.x = 0
#      if running: update()
#      if re: print("Reset"); init()
#
# print("Stop Program")
# # from vpython import *
# #
# # floor = box(pos=vector(0, -5, 0),
# #             color=color.white,
# #             length=10,
# #             height=.1,
# #             width=10)
# #
# # # the first cone
# # cone(pos=vector(-2, 2, 0),
# #      length=3,
# #      radius=1,
# #      color=vector(1, 0, 0))
# #
# # # the second cone
# # cone(pos=vector(0.4, 0.2, 0.6),
# #      color=vector(1, 1, 0))
# #
# # while True:
# #      pass
#
# # from visual import *
# # scene = display()
# # g=sphere(color=color.green)
# # b=sphere(pos=g.pos+(2.5,0,0),color=color.blue)
# # r=sphere(pos=g.pos+(-2.5,0,0),color=color.red)
# # total=ellipsoid(pos=g.pos+(0,2.5,0),size=(6.5,2,2))
# # label_a=label(text=u'q和w調整紅色的比例\na和s調整綠色的比例\nz和x調整藍色的比例',pos=g.pos-(0,3,0),border=10,color=color.black,background=color.white,font='sans')
# # label_b=label(text='(0.0,0.0,0.0)',pos=total.pos,border=10,color=color.black,background=color.white)
# # step=0.01
# # while True:
# #     key=scene.kb.getkey()
# #     if key=='q':
# #         if r.color[0]-step<0:
# #             r.color=(0,0,0)
# #         else:
# #             r.color=tuple([r.color[0]-step,r.color[1],r.color[2]])
# #     if key=='w':
# #         if r.color[0]+step>1:
# #             r.color=(1,0,0)
# #         else:
# #             r.color=tuple([r.color[0]+step,r.color[1],r.color[2]])
# #     if key=='a':
# #         if g.color[1]-step<0:
# #             g.color=(0,0,0)
# #         else:
# #             g.color=tuple([g.color[0],g.color[1]-step,g.color[2]])
# #     if key=='s':
# #         if g.color[1]+step>1:
# #             g.color=(0,1,0)
# #         else:
# #             g.color=tuple([g.color[0],g.color[1]+step,g.color[2]])
# #     if key=='z':
# #         if b.color[2]-step<0:
# #             b.color=(0,0,0)
# #         else:
# #             b.color=tuple([b.color[0],b.color[1],b.color[2]-step])
# #     if key=='x':
# #         if b.color[2]+step>1:
# #             b.color=(0,0,1)
# #         else:
# #             b.color=tuple([b.color[0],b.color[1],b.color[2]+step])
# #     total.color=tuple([r.color[0],g.color[1],b.color[2]])
# #     label_b.text=str(tuple([round(r.color[0],2),round(g.color[1],2),round(b.color[2],2)]))
# #     key=0
