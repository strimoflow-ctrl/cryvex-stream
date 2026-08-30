import time
import math
import logging
import mimetypes
import traceback
import os
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from FileStream.bot import multi_clients, work_loads, FileStream
from FileStream.config import Telegram, Server
from FileStream.server.exceptions import FIleNotFound, InvalidHash
from FileStream import utils, StartTime, __version__
from FileStream.utils.render_template import render_page

try:
    import psutil
except ImportError:
    psutil = None

routes = web.RouteTableDef()

def human_bytes(b):
    if not b:
        return "0 B"
    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{round(b / 1024, 1)} KB"
    elif b < 1024 * 1024 * 1024:
        return f"{round(b / (1024 * 1024), 1)} MB"
    else:
        return f"{round(b / (1024 * 1024 * 1024), 2)} GB"

def get_system_metrics():
    cpu_percent = 0
    ram_total_mb = 0
    ram_used_mb = 0
    ram_percent = 0
    net_sent_bytes = 0
    net_recv_bytes = 0

    if psutil:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            ram_total_mb = round(mem.total / (1024 * 1024))
            ram_used_mb = round(mem.used / (1024 * 1024))
            ram_percent = round(mem.percent)
            
            net = psutil.net_io_counters()
            net_sent_bytes = net.bytes_sent
            net_recv_bytes = net.bytes_recv
        except Exception:
            pass
    else:
        try:
            with open('/proc/meminfo') as f:
                lines = f.readlines()
            total_kb = int([l for l in lines if 'MemTotal' in l][0].split()[1])
            avail_kb = int([l for l in lines if 'MemAvailable' in l][0].split()[1])
            ram_total_mb = round(total_kb / 1024)
            ram_used_mb = round((total_kb - avail_kb) / 1024)
            ram_percent = round((ram_used_mb / ram_total_mb) * 100) if ram_total_mb else 0
        except Exception:
            pass

    return {
        "cpu_percent": cpu_percent,
        "ram_total_mb": ram_total_mb,
        "ram_used_mb": ram_used_mb,
        "ram_percent": ram_percent,
        "net_sent": human_bytes(net_sent_bytes),
        "net_recv": human_bytes(net_recv_bytes)
    }

SERVER_STATS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Naino Server Monitor</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', sans-serif; background-color: #050505; color: #fff; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
    </style>
</head>
<body class="min-h-screen p-6 md:p-12 flex flex-col items-center justify-center">
    <div class="w-full max-w-4xl space-y-6">
        <div class="flex items-center justify-between border-b border-white/10 pb-6">
            <div>
                <h1 class="text-3xl font-black uppercase tracking-widest text-white flex items-center gap-3">
                    <span class="text-[#FFD700]">⚡ NAINO</span> SERVER MONITOR
                </h1>
                <p class="text-gray-400 font-mono text-xs mt-1">REALTIME AWS EC2 & BANDWIDTH METRICS</p>
            </div>
            <div class="flex items-center gap-2 bg-green-500/10 border border-green-500/30 px-4 py-2 rounded-xl text-green-400 font-mono font-bold text-xs">
                <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                SYSTEM ONLINE
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-[#111] border border-white/10 rounded-2xl p-6 relative overflow-hidden">
                <div class="text-xs font-mono text-gray-400 uppercase tracking-wider mb-2">RAM Usage</div>
                <div class="text-3xl font-black text-white" id="ram-text">-- MB</div>
                <div class="w-full bg-white/10 h-2 rounded-full mt-4 overflow-hidden">
                    <div id="ram-bar" class="h-full bg-[#FFD700] rounded-full transition-all duration-500" style="width: 0%"></div>
                </div>
                <p class="text-xs font-mono text-gray-500 mt-2" id="ram-sub">Loading RAM metrics...</p>
            </div>

            <div class="bg-[#111] border border-white/10 rounded-2xl p-6 relative overflow-hidden">
                <div class="text-xs font-mono text-gray-400 uppercase tracking-wider mb-2">CPU Load</div>
                <div class="text-3xl font-black text-white" id="cpu-text">-- %</div>
                <div class="w-full bg-white/10 h-2 rounded-full mt-4 overflow-hidden">
                    <div id="cpu-bar" class="h-full bg-blue-500 rounded-full transition-all duration-500" style="width: 0%"></div>
                </div>
                <p class="text-xs font-mono text-gray-500 mt-2">Active Multi-Core CPU</p>
            </div>

            <div class="bg-[#111] border border-white/10 rounded-2xl p-6 relative overflow-hidden">
                <div class="text-xs font-mono text-gray-400 uppercase tracking-wider mb-2">Server Uptime</div>
                <div class="text-3xl font-black text-[#FFD700]" id="uptime-text">--</div>
                <p class="text-xs font-mono text-gray-500 mt-4">Pyrogram Engine Uptime</p>
            </div>
        </div>

        <!-- Network Bandwidth Section -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-[#111] border border-white/10 rounded-2xl p-6 relative overflow-hidden">
                <div class="flex items-center justify-between mb-2">
                    <div class="text-xs font-mono text-gray-400 uppercase tracking-wider">Outbound Bandwidth (Sent)</div>
                    <span class="text-xs font-mono text-green-400 bg-green-500/10 border border-green-500/20 px-2 py-0.5 rounded">Egress</span>
                </div>
                <div class="text-3xl font-black text-green-400" id="net-sent">--</div>
                <p class="text-xs font-mono text-gray-500 mt-2">Total Outgoing Data Transferred</p>
            </div>

            <div class="bg-[#111] border border-white/10 rounded-2xl p-6 relative overflow-hidden">
                <div class="flex items-center justify-between mb-2">
                    <div class="text-xs font-mono text-gray-400 uppercase tracking-wider">Inbound Bandwidth (Received)</div>
                    <span class="text-xs font-mono text-blue-400 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded">Ingress</span>
                </div>
                <div class="text-3xl font-black text-blue-400" id="net-recv">--</div>
                <p class="text-xs font-mono text-gray-500 mt-2">Total Incoming Data Received</p>
            </div>
        </div>

        <div class="bg-[#111] border border-white/10 rounded-2xl p-6">
            <h3 class="text-lg font-bold text-white mb-4">Connected Stream Bots</h3>
            <div id="bots-list" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 bg-black border border-white/10 rounded-xl text-gray-400 font-mono text-xs">Loading bot instances...</div>
            </div>
        </div>
    </div>

    <script>
        async function updateStats() {
            try {
                const res = await fetch('/status?json=1');
                const data = await res.json();
                
                document.getElementById('ram-text').innerText = `${data.metrics.ram_used_mb} MB`;
                document.getElementById('ram-sub').innerText = `${data.metrics.ram_used_mb} MB / ${data.metrics.ram_total_mb} MB (${data.metrics.ram_percent}%)`;
                document.getElementById('ram-bar').style.width = `${data.metrics.ram_percent}%`;

                document.getElementById('cpu-text').innerText = `${data.metrics.cpu_percent}%`;
                document.getElementById('cpu-bar').style.width = `${data.metrics.cpu_percent}%`;

                document.getElementById('uptime-text').innerText = data.uptime;

                document.getElementById('net-sent').innerText = data.metrics.net_sent || '0 B';
                document.getElementById('net-recv').innerText = data.metrics.net_recv || '0 B';

                const botList = document.getElementById('bots-list');
                botList.innerHTML = Object.entries(data.loads).map(([bot, load]) => `
                    <div class="p-4 bg-black border border-white/10 rounded-xl flex items-center justify-between">
                        <div>
                            <div class="font-bold text-white text-sm">${bot.toUpperCase()} (${data.telegram_bot})</div>
                            <div class="text-xs font-mono text-gray-500">Connected & Serving Streams</div>
                        </div>
                        <div class="px-3 py-1 bg-[#FFD700]/10 text-[#FFD700] border border-[#FFD700]/20 rounded-lg text-xs font-mono font-bold">
                            Load: ${load}
                        </div>
                    </div>
                `).join('');
            } catch (e) {
                console.error(e);
            }
        }
        updateStats();
        setInterval(updateStats, 3000);
    </script>
</body>
</html>"""

@routes.get("/status", allow_head=True)
@routes.get("/server-stats", allow_head=True)
async def root_route_handler(request: web.Request):
    metrics = get_system_metrics()
    
    if "text/html" in request.headers.get("Accept", "") and request.query.get("json") != "1":
        return web.Response(text=SERVER_STATS_HTML, content_type='text/html')

    return web.json_response(
        {
            "server_status": "running",
            "uptime": utils.get_readable_time(time.time() - StartTime),
            "telegram_bot": "@" + FileStream.username,
            "connected_bots": len(multi_clients),
            "loads": dict(
                ("bot" + str(c + 1), l)
                for c, (_, l) in enumerate(
                    sorted(work_loads.items(), key=lambda x: x[1], reverse=True)
                )
            ),
            "metrics": metrics,
            "version": __version__,
        }
    )

@routes.get("/watch/{path}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        return web.Response(text=await render_page(path), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (BadStatusLine, ConnectionResetError) as e:
        logging.warning(f"Client disconnected during watch: {e}")
        return web.Response(status=499, text="Client Closed Connection")
    except Exception as e:
        traceback.print_exc()
        logging.critical(f"Error in watch handler: {e}")
        raise web.HTTPInternalServerError(text=str(e))


@routes.get("/dl/{path}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        return await media_streamer(request, path)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (BadStatusLine, ConnectionResetError) as e:
        logging.warning(f"Client disconnected during stream: {e}")
        return web.Response(status=499, text="Client Closed Connection")
    except Exception as e:
        traceback.print_exc()
        logging.critical(f"Error in dl stream handler: {e}")
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}

async def media_streamer(request: web.Request, db_id: str):
    range_header = request.headers.get("Range", 0)
    
    from FileStream.utils.file_properties import db
    file_info = await db.get_file(db_id)
    if not file_info:
        return web.Response(status=404, text="File not found")
        
    file_ids = file_info.get("file_ids", {})
    valid_client_indices = []
    
    for idx, client in multi_clients.items():
        if str(client.id) in file_ids:
            valid_client_indices.append(idx)
            
    if not valid_client_indices:
        valid_client_indices = list(multi_clients.keys())
        
    index = min(valid_client_indices, key=lambda k: work_loads.get(k, 0))
    faster_client = multi_clients[index]
    
    if Telegram.MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.headers.get('X-FORWARDED-FOR',request.remote)}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = utils.ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    logging.debug("before calling get_file_ids")
    file_id = await utils.get_file_ids(faster_client, db_id, multi_clients, None)

    return await tg_connect.yield_file(
        file_id, index, range_header, file_info.get("file_name"), file_info.get("file_size"), file_info.get("mime_type")
    )
