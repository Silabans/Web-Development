import pandas as pd
import matplotlib.pyplot as plt
import io, base64

def build_dataframe(tasks):
    df = pd.DataFrame({
        'content': [t.content for t in tasks],
        'priority': [t.priority for t in tasks],
        'isCompleted': [t.isCompleted for t in tasks],
        'created_at': [t.created_at for t in tasks]
    })
    return df

def encode_chart():
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64

def chart_priority(df):
    fig, ax = plt.subplots()
    df.groupby('priority')['isCompleted'].value_counts().plot(kind='bar', ax=ax, color=['#ca0303', '#ffd700', '#257963' ])
    ax.set_title('Tasks by Priority')
    ax.set_xlabel('Level of Priority')
    ax.set_ylabel('Number of Tasks')
    return encode_chart()

def chart_week(df):
    fig, ax = plt.subplots()
    df['week'] = pd.to_datetime(df['created_at']).dt.isocalendar().week
    df.groupby(['week', 'priority'])['isCompleted'].sum().plot(kind='line', ax=ax, color=['#ca0303', '#ffd700', '#257963' ])
    ax.set_title('Tasks Completed per Week (based on priority)')
    ax.set_xlabel('Week')
    ax.set_ylabel('Number of Tasks')
    return encode_chart()