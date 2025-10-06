# 智慧树学习记录自动提交器使用说明

## 功能特点

- ✅ **自动生成签名**：完全复现智慧树前端JavaScript签名算法
- ✅ **智能时间管理**：基于当前时间自动生成start_date和end_date
- ✅ **批量提交**：支持批量提交多个学习记录
- ✅ **自动递增FileID**：从指定起始FileID开始自动递增
- ✅ **请求间隔控制**：避免请求过于频繁被封

## 参数说明

### 固定参数（按需求设置）
- `study_total_time`: 360 
- `end_watch_time`: 360 (观看结束时间，固定值)
- `start_watch_time`: 0 (观看开始时间，固定值)

### 动态参数
- `start_date`: 当前时间戳 - 1小时 (毫秒)
- `end_date`: 当前时间戳 (毫秒)
- `file_id`: 从 你需要学习的视频id 开始自增

### 配置参数
```python
config = {
    'uuid': '',        # 您的用户UUID
    'course_id': '',    # 课程ID
    'start_file_id': ,  # 起始文件ID
    'count': 5,                 # 提交次数
    'delay': 2,                 # 请求间隔(秒)
    'cookies': ''               # 重要：需要填入您的Cookie
}
```

## 使用步骤

### 1. 获取Cookie
1. 打开浏览器，登录智慧树
2. 按F12打开开发者工具
3. 切换到Network标签
4. 在网站上进行一次学习操作
5. 找到对应的请求，复制Cookie字符串

### 2. 配置参数
在 `generate_signature.py` 文件中修改config字典：
- `uuid`: 替换为您的用户UUID
- `course_id`: 替换为目标课程ID
- `cookies`: 填入步骤1获取的Cookie字符串

### 3. 运行程序
```bash
python generate_signature.py
```

## 请求格式

### URL
```
POST https://cloudapi.polymas.com/learningCenterAi/stuResouce/saveStuStudyRecord
```

### Headers
```
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Cookie: [您的Cookie字符串]
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
X-Requested-With: XMLHttpRequest
Origin: https://www.zhihuishu.com
Referer: https://www.zhihuishu.com/
```

### Data格式
```python
{
    'courseId': '11284392',
    'endDate': 1758547780320,
    'endWatchTime': 3600,
    'fileId': 30983324,
    'signature': '681dc516e1272a288aa7bfe868a2fc75',
    'startDate': 1758544180320, 
    'startWatchTime': 0,
    'studyTotalTime': 3600,
    'uuid': 'dDxoaWO3'
}
```

## 签名算法

### JavaScript原逻辑
```javascript
var D = "o6xpt3b#Qy$Z" + b.zhsUuid + u.query.spocCourseId + _.value + e + w + x + v + o + b.zhsUuid;
const k = Ae(D); // Ae是MD5函数
```

### Python实现
```python
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
signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
```

## 注意事项

⚠️ **重要提醒**：
1. **必须设置有效Cookie**：否则请求会失败
2. **合理控制请求频率**：建议间隔2-5秒
3. **检查UUID和CourseID**：确保参数正确
4. **遵守使用规则**：请合理使用，避免过度请求

## 错误处理

常见响应：
- `{"code":"200","message":"成功"}` - 提交成功
- `{"code":"500","message":"操作失败"}` - 可能是Cookie过期或参数错误
- 网络超时 - 检查网络连接

## 扩展功能

程序支持以下自定义：
- 修改批量提交数量
- 调整请求间隔时间
- 自定义起始FileID
- 添加更多请求头信息

## 技术实现

- **签名生成**：完全复现前端MD5算法
- **时间管理**：基于系统时间自动计算
- **HTTP请求**：使用requests库发送POST请求

- **错误处理**：完整的异常捕获和处理机制  

## License  
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.  
