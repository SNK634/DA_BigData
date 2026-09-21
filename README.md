# DA_BigData

## Đề tài
**Phân tích dữ liệu giao thông và dự đoán ùn tắc**

## Giới thiệu

Đồ án môn **Nhập môn Big Data** tập trung vào việc thu thập, lưu trữ, xử lý và phân tích dữ liệu giao thông nhằm hỗ trợ dự đoán tình trạng ùn tắc.

Hệ thống sử dụng các công nghệ Big Data như **Hadoop/HDFS** để lưu trữ dữ liệu và **Apache Spark/PySpark** để xử lý, phân tích dữ liệu giao thông theo thời gian, khu vực và mật độ phương tiện.

Sau quá trình tiền xử lý và phân tích dữ liệu, mô hình Machine Learning được xây dựng bằng **Spark MLlib** để dự đoán mức độ ùn tắc giao thông. Kết quả sau đó được trực quan hóa thông qua dashboard để hỗ trợ theo dõi và phân tích.

## Công nghệ dự kiến

- Ubuntu
- Java JDK
- Apache Hadoop
- HDFS
- Apache Spark
- PySpark
- Spark MLlib
- Python
- Pandas
- NumPy
- Matplotlib / Plotly
- Streamlit
- Git / GitHub

## Luồng xử lý

```text
Traffic Dataset
      |
      v
     HDFS
      |
      v
Apache Spark / PySpark
      |
      v
Data Preprocessing
      |
      v
Traffic Analysis
      |
      v
Feature Engineering
      |
      v
Spark MLlib
      |
      v
Congestion Prediction
      |
      v
Dashboard



DA_BigData/
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
├── docs/
│   ├── report/
│   └── slides/
├── models/
├── notebooks/
├── outputs/
│   ├── charts/
│   └── results/
├── src/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── analysis/
│   ├── model/
│   └── dashboard/
├── .gitignore
├── README.md
└── requirements.txt



