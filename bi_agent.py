import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

def init_db():
    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        date TEXT,
        product TEXT,
        region TEXT,
        revenue REAL
    )
    """)

    data = [
        ("2024-01-01", "A", "East", 1000),
        ("2024-01-02", "B", "West", 1500),
        ("2024-01-03", "A", "East", 2000),
        ("2024-01-04", "C", "South", 1800),
        ("2024-01-05", "B", "West", 2200),
    ]

    cursor.executemany(
        "INSERT INTO sales (date, product, region, revenue) VALUES (?, ?, ?, ?)",
        data
    )

    conn.commit()
    conn.close()

def nl_to_sql(question):
    prompt = f"""
你是一个数据分析专家，请将用户问题转换为SQL。

数据库表:
sales(date, product, region, revenue)

用户问题:
{question}

只返回SQL，不要解释。
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

def run_sql(sql):
    conn = sqlite3.connect("demo.db")
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def analyze_data(question, df):
    prompt = f"""
你是数据分析师，请根据数据回答问题。

问题:
{question}

数据:
{df.to_dict()}

请给出关键结论（简洁）。
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def visualize(df):
    if df.shape[1] >= 2:
        df.plot(kind="bar", x=df.columns[0], y=df.columns[1])
        plt.title("Auto Chart")
        plt.tight_layout()
        plt.savefig("chart.png")
        plt.close()

def ask_bi(question):
    print(f"\n用户问题: {question}")

    sql = nl_to_sql(question)
    print(f"\n生成SQL:\n{sql}")

    df = run_sql(sql)
    print(f"\n查询结果:\n{df}")

    insight = analyze_data(question, df)
    print(f"\n分析结论:\n{insight}")

    visualize(df)
    print("\n图表已生成: chart.png")

if __name__ == "__main__":
    init_db()
    question = "各地区的总销售额是多少？按从高到低排序"
    ask_bi(question)
