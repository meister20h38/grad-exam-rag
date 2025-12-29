import os
import subprocess

def check_marker_help():
    # CPUモードを強制（RDP落ち防止）
    my_env = os.environ.copy()
    my_env["CUDA_VISIBLE_DEVICES"] = ""
    my_env["TORCH_DEVICE"] = "cpu"

    # ヘルプを表示させるコマンド
    command = ["marker_single", "--help"]

    print("Checking marker_single usage...")
    try:
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore',
            env=my_env
        )
        print("--- コマンドのヘルプ情報 ---")
        print(result.stdout)
        
        if not result.stdout:
            print("（標準出力は空でした）")
            print("--- エラー出力 ---")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.returncode}")
        print(e.stderr)

if __name__ == "__main__":
    check_marker_help()