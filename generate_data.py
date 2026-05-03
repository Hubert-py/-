import random
import json
from datetime import datetime, timedelta
from argparse import ArgumentParser

# 窗口-菜品映射（与主程序一致）
WINDOW_DISH_MAP = {
    'W01': 'Tomato Egg + Braised Pork + Veg',
    'W02': 'Fish with Pickled Cabbage + Mapo Tofu + Rice',
    'W03': 'Beef Noodle / Soybean Paste Noodle',
    'W04': 'Fried Rice Noodle + Fried Egg',
    'W05': 'Steamed Bun + Soy Milk',
    'W06': 'Fruit Platter + Yogurt'
}

# 窗口金额范围（元）
WINDOW_PRICE_RANGE = {
    'W01': (10.0, 16.0),
    'W02': (8.5, 12.0),
    'W03': (6.0, 10.0),
    'W04': (5.0, 8.0),
    'W05': (3.0, 6.0),
    'W06': (6.5, 10.0)
}


def generate_random_timestamp(start_date="2026-05-12", days=7):
    """生成随机时间戳（在指定日期范围内的饭点）"""
    base_date = datetime.strptime(start_date, "%Y-%m-%d")
    random_day = base_date + timedelta(days=random.randint(0, days - 1))
    # 饭点：11:30-13:00 或 17:30-19:00
    meal_hour = random.choice([11, 12, 17, 18])
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    return random_day.replace(hour=meal_hour, minute=random_minute, second=random_second).strftime("%Y-%m-%d %H:%M:%S")


def generate_single_transaction(transaction_id):
    """生成单条交易记录"""
    window_id = random.choice(list(WINDOW_DISH_MAP.keys()))
    student_id = f"S{random.randint(1001, 1200)}"
    amount = round(random.uniform(*WINDOW_PRICE_RANGE[window_id]), 2)
    timestamp = generate_random_timestamp()

    return {
        "transaction_id": f"T{transaction_id:03d}",
        "student_id": student_id,
        "timestamp": timestamp,
        "window_id": window_id,
        "amount": amount
    }


def generate_data(count, output_file="test-data.json"):
    """生成指定条数的随机数据并保存"""
    if count <= 0:
        print("错误：生成条数必须是正整数！")
        return

    data = [generate_single_transaction(i + 1) for i in range(count)]

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 成功生成 {count} 条随机数据！\n📁 保存路径：{output_file}")
    except Exception as e:
        print(f"❌ 保存文件失败：{e}")


if __name__ == "__main__":
    parser = ArgumentParser(description="食堂消费随机数据生成器（命令行版）")
    parser.add_argument("-c", "--count", type=int, required=True, help="生成数据的条数（如 -c 200）")
    parser.add_argument("-o", "--output", default="test-data.json", help="输出文件名（默认：test-data.json）")
    args = parser.parse_args()

    generate_data(args.count, args.output)
