import os
import re
import requests
import platform
import subprocess
from tqdm import tqdm

class PGDownloader:
    def __init__(self, username='fish2018', repo='PG', local_target=None):
        self.username = username
        self.repo = repo
        self.branch = 'main'
        self.local_target = local_target
        self.base_url = f'https://raw.githubusercontent.com/{username}/{repo}/{self.branch}'

    def get_readme_content(self):
        """获取 README.md 内容"""
        try:
            url = f"{self.base_url}/README.md"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open('README.md', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("README.md 已保存到当前目录")
                return response.text
            else:
                raise Exception(f"获取README.md失败，状态码：{response.status_code}")
        except Exception as e:
            print(f"获取README.md失败：{e}")
            return None

    def extract_update_info(self, content):
        """提取更新信息"""
        pattern = r'```text\s*\n(.*?)\s*```'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def extract_download_url(self, content):
        """从 README.md 提取最新版本下载链接"""
        pattern = r'```bash\s*\n(.*?)\s*```'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            urls = match.group(1).strip().split('\n')
            if urls:
                return urls[0].strip()
        return None

    def download_file(self, url, filename):
        """下载文件并显示进度条"""
        print(f"开始下载：{filename}")
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filename, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            return True
        except Exception as e:
            print(f"下载出错：{e}")
            if os.path.exists(filename):
                os.remove(filename)
            return False

    def update_local_config(self):
        """更新本地配置"""
        if not self.local_target:
            return
        
        try:
            print(f'开始更新{self.local_target}目录配置到最新版本')
            # 根据操作系统选择合适的 sed 命令
            sed_command = (f'sed -i "" "s@http://127.0.0.1:10199/@http://tg.fish2018.us.kg/@g" lib/tokenm.json' 
                         if platform.system() == "Darwin" 
                         else f'sed -i "s@http://127.0.0.1:10199/@http://tg.fish2018.us.kg/@g" lib/tokenm.json')
            
            subprocess.call(
                f'cd {self.local_target} && '
                f'cp -a lib/tokentemplate.json lib/tokenm.json && '
                f'{sed_command}',
                shell=True
            )
            print("配置更新完成")
        except Exception as e:
            print(f"更新配置出错：{e}")

    def run(self):
        """运行下载程序"""
        try:
            # 1. 获取 README.md 内容
            content = self.get_readme_content()
            if not content:
                return

            # 2. 提取更新信息
            update_info = self.extract_update_info(content)
            if update_info:
                print("\n最新更新信息：")
                print(update_info)
                print("\n")
            else:
                print("未找到更新信息")
            
            # 3. 提取下载链接
            download_url = self.extract_download_url(content)
            if not download_url:
                print("未找到下载链接")
                return
            
            # 4. 下载文件
            filename = download_url.split('/')[-1]
            if not self.download_file(download_url, filename):
                return
                
            # 5. 如果指定了本地目标目录，解压文件
            if self.local_target:
                print(f"解压文件到：{self.local_target}")
                os.makedirs(self.local_target, exist_ok=True)
                subprocess.call(
                    f'cp -a {filename} {self.local_target}/ && '
                    f'cd {self.local_target} && '
                    f'unzip -o -q {filename} && '
                    f'rm -rf {filename}',
                    shell=True
                )
                
                # 6. 更新本地配置
                self.update_local_config()
                
            print("处理完成")
            
        except Exception as e:
            print(f"发生错误：{e}")

if __name__ == '__main__':
    # 使用示例
    downloader = PGDownloader(
        username='fish2018',
        repo='PG',
        local_target='pg'  # 可选，如果需要解压到本地目录
    )
    downloader.run()