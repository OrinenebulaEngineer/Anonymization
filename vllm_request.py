import json
import requests
import re
import time
import pandas as pd
import os
from tqdm import tqdm 

class Llm:
    def __init__(self):
        # self.vllm_url = "http://185.103.84.24:80/v1/chat/completions"
        self.vllm_url = "http://0.0.0.0:8000/v1/chat/completions"

    
        
        
    def vllm_inference(self, user_message,system_message):
        # Assuming config.OPEN_MODELS is a dictionary that maps model IDs to model names
        start_time = time.time()
        prompt = [{"role": "user", "content": user_message},
                            {"role": "system", "content": system_message}]

        model = "google/gemma-2-9b-it"
        # print("hi im in vllm inference")
        payload = {
            "model": model,
            "messages": prompt,  
            "max_tokens": 1000,
            "temperature": 0.5,      
            "top_p": 1,   
        }

        try:
            # Send a POST request to VLLM server
            response = requests.post(
                self.vllm_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            # print("response")
            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                # print("status code is 200")
                end_time = time.time()  
        
                print(f"Time taken for inference: {end_time - start_time} seconds")
                return response_data
            else:
                print(f"Error in response data: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error : {e}")
            return None
                 
    def clean_text(self, content):
        cleaned_content = content.strip()                          # Remove leading/trailing spaces
        cleaned_content = re.sub(r'\n+', '\n', cleaned_content)    # Collapse multiple newlines
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content)     # Optional: collapse all excessive spaces to single space
        cleaned_content = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned_content)  # Optional: remove Markdown bold **text**
        return cleaned_content
# def response_to_dataframe():
    #     output_rows = [] 
    #     whole_output = []
    #     df1 = pd.read_csv("sample_output.csv")
    #     llm = Llm()
    #     for _,row in df1.iterrows():
    #         user_input = df1["text"][0]
    #         response = llm.vllm_inference(user_message=row["text"], system_message=system_message)
    #         response = llm.vllm_inference(user_message=user_input, system_message=system_message)

    #         content = response['choices'][0]['message']['content']
    #         clean_text = llm.clean_text(content)
    #         list_clean_text = [[row["id"]] + [clean_text]]

    #         df_clean_text = pd.DataFrame(list_clean_text, columns=["id","clean_text"])
    #         whole_output.append(df_clean_text)

    #         new_line_text = re.sub(r'(وضعیت|بلی|خیر)', r'\1\n', clean_text)
    #         new_line_text = re.sub(r'```csv', '', new_line_text)
    #         new_line_text = re.sub(r'```', '', new_line_text)


    #         list_line = new_line_text.split('\n')
    #         list_line = [item.strip() for item in list_line if item.strip()]

    #         headers = list_line[0].split(',')
    #         headers = [header.strip() for header in headers]
    #         headers = ["id"] + headers  

    #         list_text = [[row["id"]] + line.split(',') for line in list_line[1:] if line.split(",") !=(' ' | "")]  
    #         try:
    #             df_temp = pd.DataFrame(list_text, columns=headers)
    #         except Exception as e:
    #             print(f"Error was accord in spliting{e}")
    #         output_rows.append(df_temp)
    #         print(output_rows)


    # # Combine all DataFrames into one
    #     df = pd.concat(output_rows, ignore_index=True) 
    #     df2 = pd.concat(whole_output,ignore_index=True)    
        
    #     df2.to_csv('response_from_gemma', index=False, encoding='utf-8-sig')    
    #     df.to_csv('legal_20_sample_entities.csv', index=False, encoding='utf-8-sig')
    #     print("Output saved to legal_20_sample_entities.csv")




def json_response_to_dataframe(response: str):

    response = re.sub(r'\n+', ' ', response).strip()
    
    lines = re.sub(r'(بلی|بله|خیر)(?=\s|$)', r'\1\n', response)
    
    print("Processed lines with newlines:\n", lines)

    # lines = re.sub(r'(بلی|بله|خیر)', r'\1\n', response)
    # print("Processed lines with newlines:\n", lines)
    
    list_lines = lines.split("\n")
    list_lines = [line.strip() for line in list_lines if line.strip()]
    
    row_output = []
    for line in list_lines:
        pattern = r"نوع موجودیت:\s*(.*?)\s+مقدار در متن:\s*(.*?)\s+وضعیت:\s*(.*)"
        cleaned_line = line.replace(",", " ")
        match = re.search(pattern, cleaned_line)

        if match:
            no_type = match.group(1)
            value = match.group(2)
            status = match.group(3)

            
            row_output.append({
                "نوع موجودیت" : no_type,
                "مقدار در متن": value,
                "وضعیت": status

            })

        else:
            print("الگو پیدا نشد")
    # print(len(row_output))
    return row_output
        




def main():
   
    
    system_message = '''
ابتدا موجودیت های نامدار را به همراه مقادیرشان شناسایی کن. موجودیت های نامدار شامل: افراد،اسامی و فامیل‌‌های خاص، مکان ها، سازمان ها، تاریخ ها و مقادیر عددی است. 
در مرحله دوم اگرمقدار موجودیت موجود بود "بلی" بگذار اگر موجود نبود "خیر" بگذار.
 اگر موجودیتی دو مقدار دارد حتما دو مقدار را جداگانه بیاور،
 اگر موجودیتی شامل اسامی اختصاری مانند آقای ع.ا. یا آقای ا.ف. فرزند ج. است، را "خیر" بگذار.
اگر نام یا نام خانوادگی کامل بعد از موجودیت آمده بود "بله" بگذار.
اگر به جای مقدار موجودیت فقط کاراکتر * بود و بعد از آن هم مقدار موجودیت خاصی ذکر نشده بود "خیر" بگذار .
اگر موجودیت‌هایی هستند که باید عددی باشند ولی بعد از آن عددی نیامده "خیر" بگذار.
مانند نمونه خروجی که در 3 ``` آمده است را بدون توضیح اضافی در فرمت csv ، بده. 
بعد از هر موجودیت یک خط جدید بگذار و با \n مشخص کن  و در هر خط یک موجودیت را با مقدارش و وضعیتش بنویس.
نمونه ورودی :
پرونده کلاسه *حوزه دو شهری شعبه *تصمیم نهایی شماره *\n\n خواهان: اقای ع. ا. ر. ن. فرزند ا. به نشانی *\n\n خوانده: اقای ا. ن. فرزند م. ب. به نشانی *\n\n خواسته: اعسار از پرداخت محکوم به\n\n ( ( \n\n رای شورا ) ) \n\n در خصوص دعوی اقای ع. ا. ر. ن. فرزند ا. بطرفیت اقای ا. ن. بخواسته اعسار وتقسیط محکوم به دادنامه شماره *مورخ 94/2/27 درپرونده کلاسه *حوزه 2 شعبه *باعنایت به محتویات پرونده وبا توجه به درخواست خواهان و باعنایت به اظهارات طرفین شهود تعرفه شده واستشهادیه منضم دادخواست خواهان که قرینه ای برعدم توانایی پرداخت دین بوده ومستندا" به مواد7و8 و11قانون نحوه اجرای محکومیتهای مالی ومواد 277 و652 قانون مدنی خواسته خواهان را وارد تشخیص وحکم بر اعسار به تقسیط محکوم به ماهیانه 2/000/000 ریال تا استهلاک کامل صادر واعلام می نماید. رای صادره حضوری وظرف 20 روز از تاریخ ابلاغ قابل تجدیدنظرخواهی در محاکم محترم عمومی حقوقی *میباشد./\n\n قاضی حوزه 2 شعبه *\n\n ح. ا. ک
مد قایدی.
نمونه خروجی:
```
نوع موجودیت: شماره پرونده (کلاسه), مقدار در متن: *, وضعیت: خیر\n
نوع موجودیت: مکان, مقدار در متن: حوزه دو شهری, وضعیت: بلی\n
نوع موجودیت: شعبه, مقدار در متن: *, وضعیت: خیر\n
نوع موجودیت: شماره تصمیم نهایی, مقدار در متن: *, وضعیت: خیر\n
نوع موجودیت: نام کامل خواهان, مقدار در متن: اقای ع. ا. ر. ن. فرزند ا., وضعیت: خیر\n
نوع موجودیت: نشانی خواهان, مقدار در متن: *, وضعیت: خیر\n
نوع موجودیت: نام کامل خوانده, مقدار در متن: اقای ا. ن. فرزند م. ب., وضعیت: خیر\n
نوع موجودیت: نشانی خوانده, مقدار در متن: *, وضعیت: خیر\n
نوع موجودیت: شماره دادنامه, مقدار در متن: *, وضعیت: خیر\n
نوع موجودیت: تاریخ, مقدار در متن: 94/2/27, وضعیت: بلی\n
نوع موجودیت: شماره پرونده (کلاسه), مقدار در متن: *, وضعیت: خیر\n
نوع موجودیت: مکان, مقدار در متن: حوزه دو شهری, وضعیت: خیر\n
نوع موجودیت: شعبه, مقدار در متن: *, وضعیت: خیر\n
نوع موجودیت: مبلغ, مقدار در متن: 2/000/000 ریال, وضعیت: بلی\n
نوع موجودیت: نام قاضی, مقدار در متن: ح. ا. ک, وضعیت: خیر\n
نوع موجودیت: شخص, مقدار در متن: مد قایدی, وضعیت: بلی

```
'''
    
#     user_input = '''
#  پرونده کلاسه *تصمیم نهایی شماره *
#   خواهان ها: 
#   1. 
#   اقای ا. ک. فرزند ن. 2. خانم ا. ک. فرزند ا. 3. خانم ش. ک. فرزند خ. با وکالت اقای م. خ. فرزند ه. به نشانی *
#   خوانده: اقای م. ر. ح. به نشانی *
#   خواسته: اعسار از پرداخت محکوم به
#   به تاریخ  پرونده کلا سه فوق دروقت فوق العاده تحت نظراست شورا با توجه به محتویات پرونده ختم رسیدگی رااعلام و به شرح ذیل مبادرت به صدور رای می نماید.
#   رای شورا
#   در خصوص دادخواست خواهان ها ا. ا. ش. ک. با وکالت م. خ. به طرفیت خوانده م. ح. به خواسته اعسار به تقسیط مبلغ 190/000/000 ریال قاضی شورا با توجه به محتویات پرونده از جمله دادخواست تقدیمی نظر به اینکه خواهان دلیل موجه و مدللی جهت اثبات ادعای خود  ارائه ننموده و استشهادیه ابرازی نیز فاقد شرایط مندرج در ماده 7و8و9 قانون نحوه محکومیتهای مالی مصوب سال 93 می باشد. لذا دعوی خواهان غیر وارد تشخیص و مستندا به مواد مذکور قانون فوق حکم به رد دعوی وی را صادر و اعلام می دارد. رای صادره حضوری و ظرف بیست روز پس از ان قابل تجدید نظرخواهی در محاکم عمومی دادگستری شهرستان *می باشد. 
#   قاضی شعبه *
#   ک.'''


#------------------------read 2000 longest data and inference with vllm and write in new file
    longest_df = pd.read_csv("cleaned_split_top_2000_longest_records.csv")
    # longest_df = pd.read_csv("Anonymization\sample_output.csv")


    llm = Llm()
    loop_start_time = time.time()
    ne_table_list = []
    for _,row in tqdm(longest_df.iterrows(), total=longest_df.shape[0], desc= "Processing Rows"):
    # for _, row in tqdm(longest_df.head(5).iterrows(), total=5, desc="Processing Rows"):

        id = row["id"]
        text = row["clean_tgit ext"]
        # text = longest_df["clean_text"][3]

        response = llm.vllm_inference(user_message=text, system_message=system_message)
        content = response['choices'][0]['message']['content']
        clean_text = llm.clean_text(content)
        print(clean_text)
    

        row_output = json_response_to_dataframe(clean_text)

        df = pd.DataFrame(row_output)
        df["id"] = id
        ne_table_list.append(df)

        row_response_df = pd.DataFrame([[id, clean_text]], columns=["id", "response_text"])
        
        if os.path.exists("response_log.csv"):
            row_response_df.to_csv("response_log.csv", mode='a', header=False, index=False , encoding='utf-8-sig')
        else:
            row_response_df.to_csv("response_log.csv", mode='w', header=True, index=False , encoding='utf-8-sig')


    te = pd.concat(ne_table_list, ignore_index=True)
    te.to_csv("new_json_response_gemma.csv", index=False, encoding='utf-8-sig')
    loop_end_time = time.time()
    print(f"whole_time is {loop_end_time - loop_start_time}" )



   

if __name__ == "__main__":
    main()

