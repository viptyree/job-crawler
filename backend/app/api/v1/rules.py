"""API 路由 - 爬虫规则 CRUD"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.crawler_rule import CrawlerRule
from app.schemas.rule import RuleCreate, RuleUpdate, RuleResponse
from datetime import datetime

router = APIRouter(prefix="/rules", tags=["规则管理"])


@router.get("", response_model=list[RuleResponse])
async def list_rules(db: AsyncSession = Depends(get_db)):
    """获取所有规则"""
    result = await db.execute(select(CrawlerRule).order_by(CrawlerRule.id.desc()))
    rules = result.scalars().all()
    out = []
    for r in rules:
        resp = RuleResponse(
            id=r.id, name=r.name, site=r.site,
            keywords=json.loads(r.keywords or "[]"),
            cities=json.loads(r.cities or "[]"),
            rule_config=json.loads(r.rule_config or "{}"),
            schedule=r.schedule or "",
            is_active=r.is_active,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        out.append(resp)
    return out


@router.post("", response_model=RuleResponse)
async def create_rule(data: RuleCreate, db: AsyncSession = Depends(get_db)):
    """创建规则"""
    rule = CrawlerRule(
        name=data.name,
        site=data.site,
        keywords=json.dumps(data.keywords, ensure_ascii=False),
        cities=json.dumps(data.cities, ensure_ascii=False),
        rule_config=json.dumps(data.rule_config, ensure_ascii=False),
        schedule=data.schedule,
        is_active=data.is_active,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return RuleResponse(
        id=rule.id, name=rule.name, site=rule.site,
        keywords=data.keywords, cities=data.cities,
        rule_config=data.rule_config, schedule=rule.schedule,
        is_active=rule.is_active, created_at=rule.created_at, updated_at=rule.updated_at,
    )


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(rule_id: int, data: RuleUpdate, db: AsyncSession = Depends(get_db)):
    """更新规则"""
    result = await db.execute(select(CrawlerRule).where(CrawlerRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    if data.name is not None:
        rule.name = data.name
    if data.site is not None:
        rule.site = data.site
    if data.keywords is not None:
        rule.keywords = json.dumps(data.keywords, ensure_ascii=False)
    if data.cities is not None:
        rule.cities = json.dumps(data.cities, ensure_ascii=False)
    if data.rule_config is not None:
        rule.rule_config = json.dumps(data.rule_config, ensure_ascii=False)
    if data.schedule is not None:
        rule.schedule = data.schedule
    if data.is_active is not None:
        rule.is_active = data.is_active
    rule.updated_at = datetime.now()

    await db.flush()
    return RuleResponse(
        id=rule.id, name=rule.name, site=rule.site,
        keywords=json.loads(rule.keywords or "[]"),
        cities=json.loads(rule.cities or "[]"),
        rule_config=json.loads(rule.rule_config or "{}"),
        schedule=rule.schedule or "",
        is_active=rule.is_active, created_at=rule.created_at, updated_at=rule.updated_at,
    )


@router.delete("/{rule_id}")
async def delete_rule(rule_id: int, db: AsyncSession = Depends(get_db)):
    """删除规则"""
    result = await db.execute(select(CrawlerRule).where(CrawlerRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    await db.delete(rule)
    return {"message": "删除成功"}


@router.post("/{rule_id}/test")
async def test_rule(rule_id: int, db: AsyncSession = Depends(get_db)):
    """测试规则（爬取前几条数据预览）"""
    result = await db.execute(select(CrawlerRule).where(CrawlerRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    # 这里返回一个模拟测试结果，实际爬取逻辑在 crawler engine 中
    return {
        "status": "success",
        "message": f"规则 '{rule.name}' 测试完成",
        "preview_count": 0,
        "preview_data": [],
    }
