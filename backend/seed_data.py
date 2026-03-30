"""插入示例数据，用于前端演示"""
import asyncio
import json
import random
from datetime import datetime, timedelta

async def seed():
    from app.database import async_session, init_db
    from app.models.job import Job
    from app.models.company import Company

    await init_db()

    titles = [
        "Python后端开发工程师", "高级Python开发", "Python全栈工程师", "Python爬虫工程师",
        "Java高级开发工程师", "Java架构师", "Spring Boot开发", "Java后端开发",
        "前端开发工程师", "React前端开发", "Vue.js开发工程师", "高级前端工程师",
        "数据分析师", "大数据开发工程师", "数据挖掘工程师", "算法工程师",
        "DevOps工程师", "运维开发工程师", "Golang开发工程师", "全栈开发工程师",
        "产品经理", "技术总监", "AI研发工程师", "机器学习工程师",
        "Android开发", "iOS开发", "测试开发工程师", "安全工程师",
    ]
    companies = [
        "字节跳动", "阿里巴巴", "腾讯", "美团", "京东", "百度", "网易", "小米",
        "华为", "快手", "滴滴", "拼多多", "蚂蚁集团", "微软中国", "谷歌中国",
        "商汤科技", "旷视科技", "大疆创新", "蔚来汽车", "理想汽车",
        "小鹏汽车", "比亚迪", "宁德时代", "海康威视", "中兴通讯",
    ]
    cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "南京", "武汉", "西安", "苏州", "长沙", "天津"]
    districts = ["朝阳区", "海淀区", "浦东新区", "南山区", "西湖区", "高新区", "雨花台区", "武昌区", ""]
    sites = ["boss", "zhilian", "qianchen", "lagou"]
    experiences = ["1-3年", "3-5年", "5-10年", "不限", "应届生", "1年以内"]
    educations = ["本科", "硕士", "大专", "博士", "不限"]
    skill_pool = [
        "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++",
        "React", "Vue", "Angular", "Node.js", "Django", "Flask", "Spring",
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
        "Docker", "Kubernetes", "AWS", "Linux", "Git", "CI/CD",
        "机器学习", "深度学习", "NLP", "大数据", "Spark", "Kafka",
        "微服务", "分布式", "高并发", "Nginx", "TensorFlow", "PyTorch",
    ]

    salary_ranges = [
        ("8-15K", 8000, 15000), ("10-20K", 10000, 20000), ("15-25K", 15000, 25000),
        ("20-35K", 20000, 35000), ("25-40K", 25000, 40000), ("30-50K", 30000, 50000),
        ("35-60K", 35000, 60000), ("40-70K", 40000, 70000), ("50-80K", 50000, 80000),
        ("15-30K·14薪", 17500, 35000), ("20-40K·13薪", 21667, 43333),
    ]

    async with async_session() as db:
        # 插入公司
        for name in companies:
            c = Company(
                name=name,
                industry=random.choice(["互联网", "人工智能", "电商", "金融科技", "智能制造", "新能源汽车", "通信", "安防"]),
                scale=random.choice(["50-150人", "150-500人", "500-2000人", "2000-5000人", "5000-10000人", "10000人以上"]),
                stage=random.choice(["A轮", "B轮", "C轮", "D轮及以上", "已上市", "不需要融资"]),
            )
            db.add(c)

        # 插入职位 - 300条模拟数据，分布在最近15天
        for i in range(300):
            salary = random.choice(salary_ranges)
            city = random.choice(cities)
            site = random.choice(sites)
            days_ago = random.randint(0, 14)
            crawled = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))

            skills = random.sample(skill_pool, k=random.randint(2, 6))

            job = Job(
                source_site=site,
                source_id=f"{site}_{i:06d}",
                title=random.choice(titles),
                company_name=random.choice(companies),
                city=city,
                district=random.choice(districts),
                salary_raw=salary[0],
                salary_min=salary[1],
                salary_max=salary[2],
                experience=random.choice(experiences),
                education=random.choice(educations),
                job_type="全职",
                skills=json.dumps(skills, ensure_ascii=False),
                description=f"我们正在寻找优秀的工程师加入团队。\n\n岗位职责：\n1. 负责核心系统的设计和开发\n2. 参与技术方案评审\n3. 持续优化系统性能和稳定性\n\n任职要求：\n1. 计算机相关专业\n2. 熟悉 {', '.join(skills[:3])} 等技术\n3. 良好的沟通和团队协作能力",
                url=f"https://example.com/job/{site}_{i}",
                crawled_at=crawled,
            )
            db.add(job)

        await db.commit()
        print(f"Seeded: {len(companies)} companies, 300 jobs")


if __name__ == "__main__":
    asyncio.run(seed())
