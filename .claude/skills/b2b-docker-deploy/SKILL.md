	---
	name: B2B-Docker-Deploy
	description: 升级 Docker 配置，支持前端、后端、数据库三端联调与一键部署。
	---
	# 指令：全栈 Docker 容器化配置
	请更新或创建以下文件，实现包含前端的完整部署方案：
	1.  **前端 Dockerfile** (`frontend/Dockerfile`):
	    - 使用多阶段构建。
	    - **构建阶段**: `node:18-alpine`，运行 `npm install` 和 `npm run build`。
	    - **运行阶段**: `nginx:alpine`。
	    - 将构建产物 `dist` 目录复制到 Nginx 目录 `/usr/share/nginx/html`。
	    - **关键**: 编写 Nginx 配置文件 `nginx.conf`，将 `/api` 路径反向代理到后端服务 `http://web:8000`，解决跨域问题。
	2.  **后端 Dockerfile** (`backend/Dockerfile`):
	    - 保持原有配置不变，确保监听 `0.0.0.0`。
	3.  **docker-compose.yml** (项目根目录):
	    - 定义三个服务: `frontend`, `web`, `db`。
	    - **frontend 服务**:
	        - 构建上下文: `./frontend`。
	        - 端口映射: `80:80`。
	        - 依赖: `depends_on: web`。
	    - **web 服务**:
	        - 构建上下文: `./backend`。
	        - 端口映射: `8000:8000` (内部通信，外部主要通过 Nginx 访问，但保留此端口方便调试)。
	        - 环境变量: 加载 `.env`。
	    - **db 服务**:
	        - 保持原有 Postgres 配置。
	4.  **Nginx 配置示例** (`frontend/nginx.conf`):
	    ```nginx
	    server {
	        listen 80;
	        location / {
	            root /usr/share/nginx/html;
	            index index.html;
	            try_files $uri $uri/ /index.html;
	        }
	        location /api {
	            proxy_pass http://web:8000; # 关键：Docker 内部网络通信
	            rewrite ^/api/(.*) /$1 break;
	        }
	    }
	    ```
	确保运行 `docker-compose up --build` 后，用户可以直接通过浏览器访问 `http://localhost` 进入前端界面。