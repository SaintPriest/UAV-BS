# UAV-BS

使用VPython開發、模擬與探討無人機蜂巢網路之替換技術

## 1. 安裝說明

Pycharm: https://www.jetbrains.com/pycharm/ (安裝時請選擇Community版本)

Python 3.9.x: https://www.python.org/downloads/release/python-3913/

## 2. 執行專案

Pycharm 以資料夾打開專案，在Python package安裝vpython套件

**為獲得較順暢的替換畫面，請開啟瀏覽器的硬體加速功能**

## 3. 參數設定

### UavBs.py 在 def \_\_init\_\_(self):

is_all_uav_curves_enabled = True  # 啟用或停用個別無人機的System rate

is_ground_coverage_enabled = True  # 啟用或停用coverage rate計算

uav_speed_up = 5 # 調整無人機飛行速度

## 4. 若localhost拒絕連線

請檢查 VPN 和 VPN Bypass 是否關閉
