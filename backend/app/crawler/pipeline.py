"""数据清洗管道"""
import re
import json
from datetime import datetime


class DataPipeline:
    """数据清洗管道：薪资解析、城市归一化、技能提取、去重"""

    def process(self, raw: dict, site: str) -> dict:
        """处理一条原始数据"""
        cleaned = {
            "source_site": site,
            "source_id": str(raw.get("source_id", "")),
            "title": (raw.get("title") or "").strip(),
            "company_name": (raw.get("company_name") or "").strip(),
            "salary_raw": raw.get("salary_raw", ""),
            "experience": (raw.get("experience") or "").strip(),
            "education": (raw.get("education") or "").strip(),
            "job_type": (raw.get("job_type") or "").strip(),
            "description": (raw.get("description") or "").strip(),
            "url": raw.get("url", ""),
            "crawled_at": datetime.now(),
        }

        # 薪资解析
        salary_min, salary_max = self.parse_salary(cleaned["salary_raw"])
        cleaned["salary_min"] = salary_min
        cleaned["salary_max"] = salary_max

        # 城市归一化
        city, district = self.parse_city(raw.get("city", ""))
        cleaned["city"] = city
        cleaned["district"] = district

        # 技能提取
        skills = raw.get("skills", [])
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except (json.JSONDecodeError, TypeError):
                skills = [s.strip() for s in skills.split(",") if s.strip()]
        if not skills and cleaned["description"]:
            skills = self.extract_skills(cleaned["description"])
        cleaned["skills"] = json.dumps(skills, ensure_ascii=False)

        return cleaned

    @staticmethod
    def parse_salary(salary_str: str) -> tuple[int | None, int | None]:
        """
        解析薪资字符串为数值（单位：元/月）
        支持格式：20-35K, 20-35K·14薪, 2-3万, 8000-12000元/月, 面议
        """
        if not salary_str:
            return None, None

        salary_str = salary_str.strip()

        # 格式: 20-35K 或 20-35K·14薪
        match = re.match(r"(\d+(?:\.\d+)?)\s*[-~至]\s*(\d+(?:\.\d+)?)\s*[Kk]", salary_str)
        if match:
            low = float(match.group(1)) * 1000
            high = float(match.group(2)) * 1000
            # 检查是否有多薪
            months_match = re.search(r"(\d+)\s*薪", salary_str)
            if months_match:
                months = int(months_match.group(1))
                low = low * months / 12
                high = high * months / 12
            return int(low), int(high)

        # 格式: 2-3万
        match = re.match(r"(\d+(?:\.\d+)?)\s*[-~至]\s*(\d+(?:\.\d+)?)\s*万", salary_str)
        if match:
            low = float(match.group(1)) * 10000
            high = float(match.group(2)) * 10000
            return int(low), int(high)

        # 格式: 8000-12000 元/月
        match = re.match(r"(\d+)\s*[-~至]\s*(\d+)", salary_str)
        if match:
            low = int(match.group(1))
            high = int(match.group(2))
            if low > 100 and high > 100:  # 确保是月薪
                return low, high

        return None, None

    @staticmethod
    def parse_city(city_str: str) -> tuple[str, str]:
        """城市归一化：'北京·朝阳区' → ('北京', '朝阳区')"""
        if not city_str:
            return "", ""

        city_str = city_str.strip()

        # 处理各种分隔符
        for sep in ["·", "-", "‐", "—", " "]:
            if sep in city_str:
                parts = city_str.split(sep, 1)
                return parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""

        return city_str, ""

    @staticmethod
    def extract_skills(description: str) -> list[str]:
        """从职位描述中提取技能关键词"""
        common_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "Go", "Golang", "Rust",
            "C++", "C#", "PHP", "Ruby", "Swift", "Kotlin", "Scala",
            "React", "Vue", "Angular", "Node.js", "Django", "Flask", "Spring",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
            "Docker", "Kubernetes", "K8s", "AWS", "Azure", "GCP",
            "Linux", "Git", "CI/CD", "Jenkins", "Nginx",
            "机器学习", "深度学习", "NLP", "人工智能", "AI", "大数据",
            "Hadoop", "Spark", "Flink", "Kafka",
            "微服务", "分布式", "高并发", "高可用",
            "HTML", "CSS", "小程序", "Flutter", "React Native",
            "TensorFlow", "PyTorch", "Pandas", "NumPy",
        ]

        found = []
        desc_upper = description.upper()
        for skill in common_skills:
            if skill.upper() in desc_upper:
                found.append(skill)

        return found[:15]  # 最多保留15个
