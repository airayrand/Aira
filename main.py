
import requests
import json
import time
import threading
import http.server
import socketserver
from urllib.parse import parse_qs
import tempfile
import uuid
import random
import re

class FacebookPoster:
    def __init__(self):
        self.running = False
        self.post_thread = None
        self.current_task_id = None
        self.active_tasks = {}
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        ]

    def randomize_content(self, content):
        """Add randomization to content to avoid duplicate detection"""
        variations = [
            lambda x: x + " 🔥",
            lambda x: x + " ✨",
            lambda x: "💯 " + x,
            lambda x: x + " 💪",
            lambda x: "🌟 " + x,
            lambda x: x + " 🚀",
            lambda x: "⚡ " + x,
            lambda x: x + " 💎",
        ]
        
        # Add random emoji variation
        if random.choice([True, False]):
            content = random.choice(variations)(content)
        
        # Add random spacing variations
        if random.choice([True, False]):
            content = content.replace(' ', '  ')  # Double space sometimes
        
        # Add random line breaks for longer content
        if len(content) > 50 and random.choice([True, False]):
            words = content.split()
            mid = len(words) // 2
            content = ' '.join(words[:mid]) + '\n\n' + ' '.join(words[mid:])
        
        return content

    def generate_random_delay(self, base_delay):
        """Generate random delay to avoid pattern detection"""
        # Random delay between 70% to 150% of base delay
        min_delay = int(base_delay * 0.7)
        max_delay = int(base_delay * 1.5)
        
        # Add extra random delays occasionally
        if random.random() < 0.3:  # 30% chance of longer delay
            max_delay = int(base_delay * 2.5)
        
        return random.randint(min_delay, max_delay)

    def stop_task(self, task_id=None):
        if task_id and task_id in self.active_tasks:
            self.active_tasks[task_id]['running'] = False
            return True
        elif self.current_task_id:
            self.running = False
            return True
        return False

    def get_active_tasks(self):
        return {k: v for k, v in self.active_tasks.items() if v['running']}

    def post_to_facebook(self, access_token, hater_name, content_lines, delay_seconds):
        task_id = str(uuid.uuid4())[:8]
        self.current_task_id = task_id
        self.active_tasks[task_id] = {
            'running': True,
            'posts_sent': 0,
            'posts_failed': 0,
            'start_time': time.time(),
            'hater_name': hater_name,
            'total_content': len(content_lines)
        }

        print(f"[+] Starting Facebook posting task (ID: {task_id})")
        print(f"[+] Hater Name: {hater_name}")
        print(f"[+] Total posts to send: {len(content_lines)}")
        print(f"[+] Base delay: {delay_seconds} seconds (randomized)")
        print("[+] Anti-blocking features enabled!")
        print("=" * 60)

        for i, content in enumerate(content_lines, 1):
            if not self.active_tasks[task_id]['running']:
                print(f"[!] Task {task_id} stopped by user")
                break

            try:
                # Randomize content to avoid duplicate detection
                randomized_content = self.randomize_content(content.strip())
                
                # Use random user agent
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }

                url = "https://graph.facebook.com/me/feed"

                # Vary the message format
                message_formats = [
                    f"{hater_name}\n\n{randomized_content}",
                    f"{hater_name} - {randomized_content}",
                    f"📢 {hater_name}\n{randomized_content}",
                    f"{hater_name}:\n\n{randomized_content}",
                    f"💬 {hater_name}\n\n{randomized_content}",
                ]
                
                full_message = random.choice(message_formats)

                data = {
                    'access_token': access_token,
                    'message': full_message
                }

                # Add random timeout between 15-45 seconds
                timeout = random.randint(15, 45)
                
                response = requests.post(url, data=data, headers=headers, timeout=timeout)
                current_time = time.strftime("%Y-%m-%d %I:%M:%S %p")

                if response.ok:
                    self.active_tasks[task_id]['posts_sent'] += 1
                    print(f"[✅] Post {i}/{len(content_lines)} sent successfully!")
                    print(f"    👤 Hater: {hater_name}")
                    print(f"    🕒 Time: {current_time}")
                    print(f"    📝 Content: {randomized_content[:50]}...")
                    print(f"    🎯 Format: Randomized")
                else:
                    self.active_tasks[task_id]['posts_failed'] += 1
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    print(f"[❌] Post {i}/{len(content_lines)} failed!")
                    print(f"    🚫 Error: {error_msg}")
                    print(f"    🔄 Status Code: {response.status_code}")

                    # Handle different error types
                    if response.status_code in [401, 403]:
                        print("[!] Access token invalid. Stopping task.")
                        break
                    elif 'spam' in error_msg.lower() or 'blocked' in error_msg.lower():
                        print("[⚠️] Content flagged as spam. Applying longer delay...")
                        extended_delay = self.generate_random_delay(delay_seconds * 3)
                        print(f"[⏳] Extended delay: {extended_delay} seconds")
                        for countdown in range(extended_delay, 0, -1):
                            if not self.active_tasks[task_id]['running']:
                                break
                            if countdown % 30 == 0 or countdown <= 10:
                                print(f"    ⏱️  {countdown} seconds remaining (spam protection)...")
                            time.sleep(1)
                    elif response.status_code == 429:  # Rate limit
                        print("[⚠️] Rate limit hit. Applying extended delay...")
                        rate_limit_delay = self.generate_random_delay(delay_seconds * 4)
                        print(f"[⏳] Rate limit delay: {rate_limit_delay} seconds")
                        for countdown in range(rate_limit_delay, 0, -1):
                            if not self.active_tasks[task_id]['running']:
                                break
                            if countdown % 60 == 0 or countdown <= 15:
                                print(f"    ⏱️  {countdown} seconds remaining (rate limit)...")
                            time.sleep(1)

                print("-" * 50)

                # Smart delay system - wait before next post (except for last post)
                if i < len(content_lines) and self.active_tasks[task_id]['running']:
                    smart_delay = self.generate_random_delay(delay_seconds)
                    
                    # Increase delay if recent failures
                    failure_rate = self.active_tasks[task_id]['posts_failed'] / i
                    if failure_rate > 0.3:  # More than 30% failure rate
                        smart_delay = int(smart_delay * 1.8)
                        print(f"[🛡️] High failure rate detected. Increasing delay to {smart_delay}s")
                    
                    print(f"[⏳] Smart delay: {smart_delay} seconds before next post...")
                    
                    for countdown in range(smart_delay, 0, -1):
                        if not self.active_tasks[task_id]['running']:
                            break
                        if countdown % 30 == 0 or countdown <= 10:
                            print(f"    ⏱️  {countdown} seconds remaining...")
                        time.sleep(1)

            except requests.exceptions.Timeout:
                print(f"[⚠️] Timeout on post {i}. Retrying with longer delay...")
                self.active_tasks[task_id]['posts_failed'] += 1
                continue
            except Exception as e:
                print(f"[!] Error posting content {i}: {str(e)}")
                self.active_tasks[task_id]['posts_failed'] += 1
                continue

        self.active_tasks[task_id]['running'] = False
        posts_sent = self.active_tasks[task_id]['posts_sent']
        posts_failed = self.active_tasks[task_id]['posts_failed']
        success_rate = (posts_sent / len(content_lines)) * 100 if content_lines else 0
        
        print(f"[!] Task {task_id} completed!")
        print(f"[📊] Results: {posts_sent}/{len(content_lines)} posted successfully ({success_rate:.1f}%)")
        print(f"[📊] Failed: {posts_failed}")

facebook_poster = FacebookPoster()

class FacebookPostHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Get active tasks for status display
            active_tasks = facebook_poster.get_active_tasks()
            status_html = ""
            if active_tasks:
                status_html = f"""
                <div class="status-panel">
                    <h4>📊 Active Tasks</h4>
                    <div class="row">
                """
                for task_id, task in active_tasks.items():
                    runtime = time.time() - task['start_time']
                    runtime_formatted = f"{int(runtime//60):02d}:{int(runtime%60):02d}"
                    success_rate = (task['posts_sent'] / task['total_content'] * 100) if task['total_content'] > 0 else 0
                    status_html += f"""
                        <div class="col-md-6 mb-3">
                            <div class="task-card">
                                <h6>Task: {task_id}</h6>
                                <p>👤 Hater: {task['hater_name']}</p>
                                <p>📝 Progress: {task['posts_sent']}/{task['total_content']}</p>
                                <p>❌ Failed: {task.get('posts_failed', 0)}</p>
                                <p>📈 Success: {success_rate:.1f}%</p>
                                <p>⏱️ Runtime: {runtime_formatted}</p>
                                <form method="post" action="/stop" style="display:inline;">
                                    <input type="hidden" name="task_id" value="{task_id}">
                                    <button type="submit" class="btn btn-sm btn-danger">Stop</button>
                                </form>
                            </div>
                        </div>
                    """
                status_html += """
                    </div>
                </div>
                """

            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>1𝘗𝘙𝘐𝘕𝘊𝘞🍾 - Anti-Block Edition</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    label {{ color: white; }}
    .file {{ height: 30px; }}
    body {{
      background-image: url('https://i.postimg.cc/2j4Nw3PT/IMG-20250524-WA0013.jpg');
      background-size: cover;
      background-repeat: no-repeat;
      background-position: center center;
      background-attachment: fixed;
      min-height: 100vh;
      color: white;
    }}
    .container {{
      max-width: 400px;
      height: auto;
      border-radius: 20px;
      padding: 20px;
      box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
      border: none;
      resize: none;
    }}
    .form-control {{
      outline: 1px blue;
      border: 1px double #C51077;
      background: transparent;
      width: 100%;
      height: 40px;
      padding: 10px;
      margin-bottom: 15px;
      border-radius: 5px;
      color: white;
    }}
    .form-control::placeholder {{ color: #C51077; }}
    .header {{ text-align: center; padding-bottom: 20px; }}
    .btn-submit {{ width: 100%; margin-top: 20px; }}
    .footer {{ text-align: center; margin-top: 20px; color: #C51077; }}
    .whatsapp-link {{
      display: inline-block;
      color: #C51077;
      text-decoration: none;
      margin-top: 10px;
    }}
    .whatsapp-link i {{ margin-right: 5px; }}
    .alert {{ margin-top: 10px; }}
    .status-panel {{
      background: rgba(255, 255, 255, 0.1);
      border-radius: 15px;
      padding: 20px;
      margin-bottom: 20px;
      backdrop-filter: blur(10px);
    }}
    .task-card {{
      background: rgba(197, 16, 119, 0.2);
      border: 1px solid #C51077;
      border-radius: 10px;
      padding: 15px;
    }}
    .task-card h6 {{ color: #C51077; font-weight: bold; }}
    .task-card p {{ margin: 5px 0; font-size: 0.9rem; }}
    .anti-block-info {{
      background: rgba(76, 175, 80, 0.2);
      border: 1px solid #4CAF50;
      border-radius: 10px;
      padding: 15px;
      margin-bottom: 20px;
      font-size: 0.9rem;
    }}
    .anti-block-info h6 {{ color: #4CAF50; margin-bottom: 10px; }}
  </style>
</head>
<body>
  <header class="header mt-4">
    <h1 class="mt-3">FEEL THE POWER OF YOUR DAD</h1>
    <p class="text-success">🛡️ Anti-Block Edition</p>
  </header>
  <div class="container text-center">
    <div class="anti-block-info">
      <h6>🛡️ Anti-Block Features Enabled:</h6>
      <small>
        • Content randomization with emojis<br>
        • Smart delay system (70%-150% of set time)<br>
        • Random user agents & headers<br>
        • Spam detection & auto-recovery<br>
        • Rate limit protection<br>
        • Multiple message formats
      </small>
    </div>
    {status_html}
    <form method="post" enctype="multipart/form-data" action="/start">
      <div class="mb-3">
        <label for="accessToken" class="form-label">Facebook Access Token</label>
        <input type="password" class="form-control" id="accessToken" name="accessToken" placeholder="Enter your token" required>
      </div>
      <div class="mb-3">
        <label for="haterName" class="form-label">Hater Name</label>
        <input type="text" class="form-control" id="haterName" name="haterName" placeholder="Enter hater name" required>
      </div>
      <div class="mb-3">
        <label for="time" class="form-label">Base Time Delay (seconds)</label>
        <input type="number" class="form-control" id="time" name="time" min="30" value="120" required>
        <small class="text-light">Recommended: 120+ seconds (will be randomized)</small>
      </div>
      <div class="mb-3">
        <label for="contentFile" class="form-label">Post Content File (.txt)</label>
        <input type="file" class="form-control" id="contentFile" name="contentFile" accept=".txt" required>
        <small class="text-light">Upload a .txt file with each line being a separate post</small>
      </div>
      <button type="submit" class="btn btn-primary btn-submit">Start Smart Posting</button>
    </form>
  </div>

  <footer class="footer">
    <p>© 2025 Rishab Sbr ka baap - Anti-Block Edition</p>
    <p>Haters <a href="https://www.facebook.com/profile.php?id=100088122849082">FB</a></p>
    <div class="mb-3">
      <a href="https://www.facebook.com/profile.php?id=100088122849082" class="whatsapp-link">
        <i class="fab fa-facebook"></i> Chat on FB
      </a>
    </div>
  </footer>
</body>
</html>"""
            self.wfile.write(html_content.encode())

        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            active_tasks = facebook_poster.get_active_tasks()
            self.wfile.write(json.dumps(active_tasks).encode())

    def do_POST(self):
        if self.path == '/stop':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(post_data)

            task_id = form_data.get('task_id', [None])[0]
            stopped = facebook_poster.stop_task(task_id)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            status_message = "✅ Task Stopped Successfully!" if stopped else "ℹ️ No Active Task Found"

            response_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Task Control</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; }}
                    .alert-container {{ max-width: 500px; margin: 0 auto; }}
                    .alert {{ border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="alert-container">
                        <div class="alert alert-success text-center">
                            <h2>{status_message}</h2>
                            <a href="/" class="btn btn-primary btn-lg mt-3">Return to App</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(response_html.encode())
            return

        # Handle form submission for starting posting
        try:
            form_data = {}
            content_length = int(self.headers.get('Content-Length', 0))

            if content_length > 0:
                boundary = self.headers.get('Content-Type', '').split('boundary=')[-1]
                if boundary:
                    post_data = self.rfile.read(content_length)

                    # Simple multipart parsing
                    parts = post_data.split(f'--{boundary}'.encode())

                    for part in parts:
                        if b'Content-Disposition' in part and b'name=' in part:
                            lines = part.split(b'\r\n')
                            name = None
                            content = b''

                            for i, line in enumerate(lines):
                                if b'Content-Disposition' in line and b'name=' in line:
                                    name_start = line.find(b'name="') + 6
                                    name_end = line.find(b'"', name_start)
                                    name = line[name_start:name_end].decode()
                                elif line == b'' and i > 0:
                                    content = b'\r\n'.join(lines[i+1:])
                                    if content.endswith(b'\r\n'):
                                        content = content[:-2]
                                    break

                            if name and content:
                                if name == 'contentFile':
                                    form_data[name] = content.decode('utf-8')
                                else:
                                    form_data[name] = content.decode('utf-8')

            access_token = form_data.get('accessToken')
            hater_name = form_data.get('haterName')
            delay = int(form_data.get('time', 120))
            content_data = form_data.get('contentFile', '')

            if not all([access_token, hater_name, content_data]):
                raise ValueError("Missing required fields")

            content_lines = [line.strip() for line in content_data.split('\n') if line.strip()]

            if not content_lines:
                raise ValueError("Content file is empty or invalid")

            # Minimum delay warning
            if delay < 60:
                print("[⚠️] Warning: Delay less than 60 seconds may increase blocking risk")

            # Start posting task in background thread
            post_thread = threading.Thread(
                target=facebook_poster.post_to_facebook,
                args=(access_token, hater_name, content_lines, delay)
            )
            post_thread.daemon = True
            post_thread.start()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            success_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Smart Posting Started</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); min-height: 100vh; display: flex; align-items: center; }}
                    .alert-container {{ max-width: 600px; margin: 0 auto; }}
                    .alert {{ border-radius: 15px; padding: 40px; box-shadow: 0 15px 40px rgba(0,0,0,0.2); }}
                    .feature-list {{ text-align: left; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="alert-container">
                        <div class="alert alert-success text-center">
                            <h2>🚀 Smart Posting Started!</h2>
                            <div class="row text-center mt-4">
                                <div class="col-md-4">
                                    <h5>👤 Hater</h5>
                                    <p class="h4">{hater_name}</p>
                                </div>
                                <div class="col-md-4">
                                    <h5>📝 Posts</h5>
                                    <p class="h4">{len(content_lines)}</p>
                                </div>
                                <div class="col-md-4">
                                    <h5>⏱️ Base Delay</h5>
                                    <p class="h4">{delay}s</p>
                                </div>
                            </div>
                            <div class="feature-list">
                                <h6>🛡️ Active Anti-Block Features:</h6>
                                <ul>
                                    <li>✅ Content randomization with emojis</li>
                                    <li>✅ Smart delay system (±50% variation)</li>
                                    <li>✅ Random user agents</li>
                                    <li>✅ Spam detection & recovery</li>
                                    <li>✅ Rate limit protection</li>
                                    <li>✅ Multiple message formats</li>
                                </ul>
                            </div>
                            <p class="mt-3">Check the console for real-time updates</p>
                            <a href="/" class="btn btn-primary btn-lg mt-3">View Dashboard</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); min-height: 100vh; display: flex; align-items: center; }}
                    .alert-container {{ max-width: 500px; margin: 0 auto; }}
                    .alert {{ border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="alert-container">
                        <div class="alert alert-danger text-center">
                            <h2>❌ Error</h2>
                            <p class="h5">{str(e)}</p>
                            <a href="/" class="btn btn-primary mt-3">Go Back</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())

def start_server():
    PORT = 5000
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), FacebookPostHandler) as httpd:
            print("=" * 60)
            print(f"🚀 Facebook Smart Posting App Started! (Anti-Block Edition)")
            print(f"📡 Server URL: http://0.0.0.0:{PORT}")
            print("=" * 60)
            print("✨ New Anti-Block Features:")
            print("   • Content randomization with emojis")
            print("   • Smart delay system (70%-150% variation)")
            print("   • Random user agents & headers")
            print("   • Spam detection & auto-recovery")
            print("   • Rate limit protection")
            print("   • Multiple message formats")
            print("   • Enhanced error handling")
            print("=" * 60)
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\n[!] Server stopped gracefully.")

if __name__ == '__main__':
    main()
