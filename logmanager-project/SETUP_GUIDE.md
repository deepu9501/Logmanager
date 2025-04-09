# सर्वर लॉग मैनेजमेंट सिस्टम: सेटअप गाइड

इस गाइड में आपको स्टेप-बाय-स्टेप बताया गया है कि इस प्रोजेक्ट को कैसे सेटअप और रन करें।

## आवश्यकताएँ

- Python 3.8 या इससे ऊपर
- PostgreSQL डेटाबेस
- Redis (WebSockets और Celery के लिए)

## सेटअप स्टेप्स

### 1. वर्चुअल एनवायरनमेंट बनाएं और एक्टिवेट करें

```bash
# Windows पर
python -m venv venv
venv\Scripts\activate

# Linux/Mac पर
python -m venv venv
source venv/bin/activate
```

### 2. डिपेंडेंसी इंस्टॉल करें

```bash
pip install -r requirements.txt
```

### 3. PostgreSQL डेटाबेस सेटअप करें

1. PostgreSQL इंस्टॉल करें (अगर पहले से इंस्टॉल नहीं है)
2. एक नया डेटाबेस बनाएं:
   ```sql
   CREATE DATABASE logmanager;
   ```
3. `logmanager/settings.py` में डेटाबेस सेटिंग्स अपडेट करें:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'logmanager',  # डेटाबेस का नाम
           'USER': 'postgres',    # आपका PostgreSQL यूजरनेम
           'PASSWORD': 'password', # आपका PostgreSQL पासवर्ड
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

### 4. डायरेक्टरी स्ट्रक्चर सुनिश्चित करें

निम्नलिखित डायरेक्टरीज़ होनी चाहिए:
- `static/` - स्टैटिक फाइल्स के लिए
- `media/` - अपलोड की गई फाइल्स के लिए
- `logs/` - लॉग्स के लिए
- `templates/` - टेम्पलेट्स के लिए

### 5. माइग्रेशन और सुपरयूजर बनाएं

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. स्टैटिक फाइल्स को कलेक्ट करें

```bash
python manage.py collectstatic
```

### 7. Redis सर्वर शुरू करें

Redis सर्वर स्थापित करें और उसे शुरू करें। Windows पर, आप [Windows के लिए Redis](https://github.com/microsoftarchive/redis/releases) इस्तेमाल कर सकते हैं।

### 8. Celery वर्कर्स शुरू करें

नए टर्मिनल विंडो में:
```bash
celery -A logmanager worker -l info
```

नए टर्मिनल विंडो में (अगर बीट स्केड्यूलिंग चाहिए):
```bash
celery -A logmanager beat -l info
```

### 9. डेवलपमेंट सर्वर शुरू करें

```bash
python manage.py runserver
```

### 10. अब आप निम्नलिखित URL पर एक्सेस कर सकते हैं:

- Admin पैनल: http://localhost:8000/admin/
- API Endpoints: http://localhost:8000/api/

## प्रारंभिक डेटा सेटअप

Admin पैनल (http://localhost:8000/admin/) में लॉग इन करें और निम्नलिखित बनाएं:
1. Log Sources (लॉग स्रोत)
2. Notification Templates (नोटिफिकेशन टेम्पलेट्स)
3. Notification Channels (नोटिफिकेशन चैनल्स)

## समस्या निवारण

अगर आपको कोई समस्या आती है, तो निम्नलिखित जांचें:
1. PostgreSQL सर्वर चल रहा है
2. Redis सर्वर चल रहा है
3. सभी डिपेंडेंसीज सही ढंग से इंस्टॉल हैं
4. `logmanager/settings.py` में सही कॉन्फ़िगरेशन है

अधिक जानकारी के लिए, README.md फाइल देखें। 