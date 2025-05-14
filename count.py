import pandas as pd
import numpy as np

# 读取原始数据并保留列结构
data = pd.read_csv(r'D:\vscode\python\homework\English\main\score.csv')
original_columns = data.columns.tolist()  # 获取原始列名

# 提取需要处理的6个指标数据（排除首列）
processing_data = data.iloc[:, 1:]

# ================== 熵权法计算部分 ==================
# 定义指标方向：前两列为成本型，其余为效益型
directions = [ 1,1,1, 1, 1,1]

# 数据标准化处理
normalized_data = np.zeros(processing_data.shape)
for i in range(processing_data.shape[1]):
    col_data = processing_data.iloc[:, i]
    max_val = col_data.max()
    min_val = col_data.min()
    range_val = max_val - min_val
    
    if range_val == 0:  # 处理常数列
        normalized_data[:, i] = 0.5  # 统一赋中间值
    else:
        if directions[i] == -1:  # 成本型指标
            normalized_col = (max_val - col_data) / range_val
        else:  # 效益型指标
            normalized_col = (col_data - min_val) / range_val
        normalized_data[:, i] = normalized_col + 1e-6  # 避免零值

# 计算熵值
epsilon = 1e-6  # 防止log(0)
p_matrix = normalized_data / np.sum(normalized_data, axis=0)
entropy = -np.sum(p_matrix * np.log(p_matrix + epsilon), axis=0) / np.log(len(data))

# 计算最终权重
weights = (1 - entropy) / np.sum(1 - entropy)
# ===================================================

# ================== 综合得分计算 ==================
# 计算每个样本的综合得分（加权求和）
composite_scores = np.dot(normalized_data, weights)

# 将计算结果写入原始数据的第一列
data[original_columns[0]] = composite_scores  # 更新transportation列

data.to_csv(f'{original_columns[0]}_result.csv', index=False)

# ================== 结果展示 ==================
print("各指标权重计算结果：")
for col_name, weight in zip(processing_data.columns, weights):
    print(f"{col_name.ljust(30)}: {weight:.6f}")

print("\n前3行计算结果示例：")
print(data.head(3).to_markdown(index=False))

print("\n结果已保存至 environment_result.csv，其中首列为综合得分")