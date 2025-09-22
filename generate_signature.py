#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import time
import requests
import json
from datetime import datetime

def generate_signature(uuid, course_id, file_id, study_total_time, start_date, end_date, end_watch_time, start_watch_time):
    """
    根据智慧树JS逻辑生成签名
    
    JS原逻辑:
    var D = "o6xpt3b#Qy$Z" + b.zhsUuid + u.query.spocCourseId + _.value + e + w + x + v + o + b.zhsUuid;
    
    参数映射:
    b.zhsUuid -> uuid
    u.query.spocCourseId -> course_id  
    _.value -> file_id
    e -> study_total_time
    w -> start_date
    x -> end_date
    v -> end_watch_time
    o -> start_watch_time
    """
    
    # 构造待加密字符串
    sign_string = (
        "o6xpt3b#Qy$Z" + 
        str(uuid) + 
        str(course_id) + 
        str(file_id) + 
        str(study_total_time) + 
        str(start_date) + 
        str(end_date) + 
        str(end_watch_time) + 
        str(start_watch_time) + 
        str(uuid)
    )
    
    # MD5加密
    md5_hash = hashlib.md5()
    md5_hash.update(sign_string.encode('utf-8'))
    signature = md5_hash.hexdigest()
    
    return signature

def generate_time_params():
    """
    生成时间相关参数
    end_date: 当前时间戳(毫秒)
    start_date: 当前时间戳 - 1小时(毫秒)
    """
    current_time_ms = int(time.time() * 1000)  # 当前时间戳(毫秒)
    end_date = current_time_ms
    start_date = current_time_ms - (60 * 60 * 1000)  # 减去1小时
    
    return start_date, end_date

def send_study_record(uuid, course_id, file_id, cookies=None, authorization=None, start_watch_time=0, end_watch_time=360, study_total_time=360):
    """
    发送学习记录请求
    """
    # 生成时间参数
    start_date, end_date = generate_time_params()
    # 生成签名
    signature = generate_signature(
        uuid=uuid,
        course_id=course_id,
        file_id=file_id,
        study_total_time=study_total_time,
        start_date=start_date,
        end_date=end_date,
        end_watch_time=end_watch_time,
        start_watch_time=start_watch_time
    )
    
    # 构造请求数据 - 改为JSON格式
    data = {
        'courseId': course_id,
        'endDate': end_date,
        'endWatchTime': end_watch_time,
        'fileId': file_id,
        'signature': signature,
        'startDate': start_date,
        'startWatchTime': start_watch_time,
        'studyTotalTime': study_total_time,
        'uuid': uuid
    }
    
    # 请求头 - 根据真实抓包更新
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'Origin': 'https://hike-teaching-center.polymas.com',
        'Pragma': 'no-cache',
        'Priority': 'u=1, i',
        'Referer': 'https://hike-teaching-center.polymas.com/',
        'Route': '/tools-hike/studentStudyResource',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="136", "Google Chrome";v="136"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'Zhsuid': ''
    }
    if not headers['Zhsuid'] :
        print("请设置Zhsuid请求头,否则请求会失败,从浏览器抓包获得")
        exit(1)
    # 添加Authorization头
    if authorization:
        headers['Authorization'] = authorization
    
    # 如果提供了cookies，添加到headers
    if cookies:
        headers['Cookie'] = cookies
    
    url = 'https://cloudapi.polymas.com/learningCenterAi/stuResouce/saveStuStudyRecord'
    
    print(f"=== 发送学习记录 ===")
    print(f"FileID: {file_id}")
    print(f"开始时间: {datetime.fromtimestamp(start_date/1000).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"结束时间: {datetime.fromtimestamp(end_date/1000).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"签名: {signature}")
    print(f"请求数据: {data}")
    
    try:
        # 发送JSON数据而不是form数据
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

def batch_send_records(uuid, course_id, start_file_id, count=5, cookies=None, authorization=None, delay=2):
    """
    批量发送学习记录
    
    Args:
        uuid: 用户UUID
        course_id: 课程ID
        start_file_id: 起始文件ID
        count: 发送次数
        cookies: Cookie字符串
        authorization: Authorization token
        delay: 请求间隔时间(秒)
    """
    results = []
    interval = 360
    # 360 就是最大间隔时长，请不要随便修改
    repeat = 3
    for r in range(repeat):
        start_watch_time = r * interval
        end_watch_time = (r + 1) * interval
        study_total_time = end_watch_time - start_watch_time
        for i in range(count):
            current_file_id = start_file_id + i
            print(f"\n{'='*50}")
            print(f"第 {r*count + i + 1}/{repeat*count} 次请求（第{r+1}轮，第{i+1}个fileId）")
            response = send_study_record(
                uuid, course_id, current_file_id,
                cookies, authorization,
                start_watch_time=start_watch_time,
                end_watch_time=end_watch_time,
                study_total_time=study_total_time
            )
            results.append({
                'file_id': current_file_id,
                'round': r+1,
                'start_watch_time': start_watch_time,
                'end_watch_time': end_watch_time,
                'success': response is not None and response.status_code == 200,
                'response': response.text if response else None
            })
            # 延迟下次请求
            if not (r == repeat-1 and i == count-1):
                print(f"等待 {delay} 秒...")
                time.sleep(delay)
    return results

def main():
    # 配置参数 - 从抓包数据更新
    config = {
        'uuid': '',  # 从网页获取uid
        'course_id': '11284392',  # 请替换为您的课程ID
        'start_file_id': 30983322,  # 起始文件ID
        'count': 52,  # 发送次数
        'delay': 2,  # 请求间隔(秒)
        # 从抓包数据中获取的完整Cookie
        'cookies': '',
        # 从抓包数据中获取的Authorization token
        'authorization': ''
    }
    
    print("=== 智慧树学习记录自动提交器 ===")
    print("360s就是最大间隔时长，请不要随便修改")
    print("配置信息:")
    for key, value in config.items():
        if key in ['cookies', 'authorization']:
            print(f"  {key}: {'已设置' if value else '未设置'}")
            if not value:
                print(f"    请从浏览器抓包数据中获取并设置{key}，否则请求会失败。")
                exit(1)
        else:
            print(f"  {key}: {value}")
    
    print(f"\n开始批量发送学习记录...")
    
    # 批量发送
    results = batch_send_records(
        uuid=config['uuid'],
        course_id=config['course_id'],
        start_file_id=config['start_file_id'],
        count=config['count'],
        cookies=config['cookies'],
        authorization=config['authorization'],
        delay=config['delay']
    )
    
    # 统计结果
    success_count = sum(1 for r in results if r['success'])
    print(f"\n{'='*50}")
    print(f"执行完成!")
    print(f"总请求数: {len(results)}")
    print(f"成功数量: {success_count}")
    print(f"失败数量: {len(results) - success_count}")
    
    # 显示详细结果
    print(f"\n详细结果:")
    for i, result in enumerate(results):
        status = "✓" if result['success'] else "✗"
        print(f"  {i+1}. FileID {result['file_id']}: {status}")
        # 显示响应内容（简化版）
        if result['response']:
            try:
                resp_json = json.loads(result['response'])
                print(f"      响应: {resp_json.get('code', 'Unknown')} - {resp_json.get('message', 'No message')}")
            except:
                print(f"      响应: {result['response'][:100]}...")  # 只显示前100个字符

if __name__ == "__main__":
    main()