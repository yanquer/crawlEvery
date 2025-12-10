# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import StaleElementReferenceException
# import subprocess
#
#
# class ChromeInstance:
#     def __init__(self, url="https://www.huya.com/16868", debug_port=9222, user_data_dir="chrome-data", chrome_path=r"chrome/chrome-win64/chrome.exe"):
#         """创建Chrome浏览器实例
#         Args:
#             url (str): 启动时打开的URL地址
#             debug_port (int): 远程调试端口
#             user_data_dir (str): 用户数据目录
#             chrome_path (str): Chrome浏览器可执行文件路径
#         """
#         self.url = url
#         self.debug_port = debug_port
#         self.user_data_dir = user_data_dir
#         self.chrome_path = chrome_path
#         self.process = None
#
#     def start(self,):
#         """启动Chrome浏览器
#         Returns:
#             bool: 启动 成功 True | 失败 False
#         """
#         cmd = [
#             self.chrome_path,
#             f"--remote-debugging-port={self.debug_port}",     # 启用远程调试
#             f"--user-data-dir={self.user_data_dir}",          # 指定用户数据目录
#             "--no-first-run",                                 # 跳过首次运行提示
#             "--no-default-browser-check",                     # 跳过默认浏览器检查
#             "--disable-blink-features=AutomationControlled",  # 隐藏自动化控制标志
#             "--disable-infobars",                             # 禁用信息栏
#             "--disable-popup-blocking",                       # 禁用弹出窗口阻止
#             "--mute-audio",                                   # 静音
#             self.url,                                         # 自动打开页面
#         ]
#         try:
#             self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#             return True
#         except Exception as e:
#             print(f"启动Chrome浏览器失败: {e}")
#             return False
#
# class ChromeController:
#     def __init__(self, driver=None, debug_port=9222, driver_path=r"chrome/chromedriver-win64/chromedriver.exe"):
#         """附加到已运行的Chrome浏览器实例
#         Args:
#             driver (webdriver.Chrome | None): 已存在的Chrome WebDriver实例
#             debug_port (int): 远程调试端口
#             driver_path (str): ChromeDriver可执行文件路径
#         """
#         self.debug_port = debug_port
#         self.driver_path = driver_path
#         self.driver = driver
#         self.element = None
#
#     def _find_element(self,):
#         if not self.driver:
#             print("请先附加到浏览器实例。")
#             return None
#         try:
#             out_iframes = WebDriverWait(self.driver, 1).until(
#                 EC.presence_of_all_elements_located((By.TAG_NAME, "iframe"))
#             )
#             for outframe in out_iframes:
#                 try:
#                     self.driver.switch_to.frame(outframe)
#                     inner_iframes = WebDriverWait(self.driver, 1).until(
#                         EC.presence_of_all_elements_located((By.TAG_NAME, "iframe"))
#                     )
#                     for inframe in inner_iframes:
#                         try:
#                             self.driver.switch_to.frame(inframe)
#                             element = WebDriverWait(self.driver, 1).until(
#                                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-901oao"))
#                             )
#                             if element:
#                                 self.element = element
#                                 print('计时器元素捕获成功')
#                                 return True
#                         except Exception as e:
#                             continue
#                 except Exception as e:
#                     self.driver.switch_to.default_content()
#                     continue
#             print("未找到计时器元素")
#             return False
#         except Exception as e:
#             self.driver.switch_to.default_content()
#             return False
#
#     def attach(self):
#         """附加到已运行的Chrome浏览器实例
#         Returns:
#             webdriver.Chrome | None: 成功返回Chrome WebDriver实例，失败返回None
#         """
#         if self.driver:
#             return self.driver
#         chrome_options = Options()
#         chrome_options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")  # 连接到远程调试端口
#         chrome_options.add_argument("--ignore-certificate-errors")  # 忽略证书错误
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         try:
#             service = ChromeService(executable_path=self.driver_path)
#             self.driver = webdriver.Chrome(service=service, options=chrome_options)
#             print("成功附加到Chrome浏览器")
#             return self.driver
#         except Exception as e:
#             print(f"附加到浏览器失败: {e}")
#             return None
#
#
#     def _avaliable(self):
#         """检查当前是否可查询
#         Returns:
#             bool: 可以查询 True | 不可查询 False
#         """
#         try:
#             # 检查元素是否仍然可用
#             if self.element:
#                 # 尝试获取元素ID来验证是否仍然有效
#                 _ = self.element.get_attribute('class')
#                 return True
#             else:
#                 return self._find_element()
#         except StaleElementReferenceException:
#             # 元素过时，重新查找
#             self.element = None
#             return self._find_element()
#
#     def getTime(self) -> str:
#         """获取计时器当前时间
#         Returns:
#             str: 当前时间字符串 | wait 计时器不可用,请等待
#         """
#         if not self._avaliable():
#             return "wait"
#         return self.element.text
#
# if __name__ == "__main__":
#     chrome = ChromeInstance()
#     if not chrome.start():
#         print("启动Chrome浏览器失败。")
#         exit(1)
#
#     input("先在页面中打开小程序,再按Enter键附加到浏览器...")
#
#     controller = ChromeController()
#     # 在已创建了webdriver的情况下,也可以用下面的方式创建ChromeController实例
#     # controller = ChromeController(driver)
#     if not controller.attach():
#         print("附加到浏览器失败。")
#         exit(1)
#     import time
#     while True:
#         print('计时器时间:', controller.getTime())
#         time.sleep(1)
#
