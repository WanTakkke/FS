from sqlalchemy.ext.asyncio import AsyncSession

from mapper import employmentMapper
from models.employmentInfo import EmploymentInfo
from schema.employmentSchema import (
    EmploymentResponse,
    EmploymentRequest,
    EmploymentUpdateRequest,
    EmploymentQueryRequest,
)
from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


async def get_employment(db: AsyncSession, page: int, page_size: int):
    logger.info("Service就业分页查询: page=%s, page_size=%s", page, page_size)
    skip = (page - 1) * page_size
    result = await employmentMapper.get_employment(db, skip, page_size)
    logger.info("Service就业分页查询完成: count=%s", len(result))
    return [EmploymentResponse.model_validate(item) for item in result]


async def get_employment_by_conditions(db: AsyncSession, query_params: EmploymentQueryRequest):
    logger.info("Service就业多条件查询: page=%s, page_size=%s", query_params.page, query_params.page_size)
    skip = (query_params.page - 1) * query_params.page_size
    result = await employmentMapper.get_employment_by_conditions(db, query_params, skip, query_params.page_size)
    logger.info("Service就业多条件查询完成: count=%s", len(result))
    return [EmploymentResponse.model_validate(item) for item in result]


async def get_employment_detail(db: AsyncSession, employment_id: int):
    logger.info("Service就业详情查询: id=%s", employment_id)
    result = await employmentMapper.get_employment_detail(db, employment_id)
    if not result:
        logger.warning("Service就业详情查询失败: 记录不存在 id=%s", employment_id)
        raise ValueError(f"就业记录ID {employment_id} 不存在")
    logger.info("Service就业详情查询成功: id=%s", employment_id)
    return EmploymentResponse.model_validate(result)


async def create_employment(db: AsyncSession, employment_data: EmploymentRequest):
    logger.info(
        "Service新增就业记录: student_code=%s, company_name=%s",
        employment_data.student_code,
        employment_data.company_name
    )

    student = await employmentMapper.get_student_by_code(db, employment_data.student_code)
    if not student:
        logger.warning("Service新增就业记录失败: 学生不存在 student_code=%s", employment_data.student_code)
        raise ValueError(f"学生编号 {employment_data.student_code} 不存在")

    duplicate = await employmentMapper.get_employment_by_unique_key(
        db,
        student.id,
        employment_data.company_name,
        employment_data.job_open_date
    )
    if duplicate:
        logger.warning(
            "Service新增就业记录失败: 记录已存在 student_code=%s, company_name=%s",
            employment_data.student_code,
            employment_data.company_name
        )
        raise ValueError("相同学生、公司、开放时间的就业记录已存在")

    if employment_data.is_latest_employment:
        await employmentMapper.clear_current_employment(db, student.id)

    employment_info = EmploymentInfo(
        student_id=student.id,
        company_name=employment_data.company_name,
        job_open_date=employment_data.job_open_date,
        offer_date=employment_data.offer_date,
        salary=employment_data.salary,
        is_current=1 if employment_data.is_latest_employment else 0
    )
    created = await employmentMapper.create_employment(db, employment_info)
    result = await employmentMapper.get_employment_detail(db, created.id)
    logger.info("Service新增就业记录成功: id=%s", created.id)
    return EmploymentResponse.model_validate(result)


async def update_employment(db: AsyncSession, employment_data: EmploymentUpdateRequest):
    logger.info("Service修改就业记录: id=%s", employment_data.id)
    existing = await employmentMapper.get_employment_by_id(db, employment_data.id)
    if not existing:
        logger.warning("Service修改就业记录失败: 记录不存在 id=%s", employment_data.id)
        raise ValueError(f"就业记录ID {employment_data.id} 不存在")

    update_fields = employment_data.model_dump(exclude_unset=True, exclude={"id"})
    target_student_id = existing.student_id

    if "student_code" in update_fields:
        student = await employmentMapper.get_student_by_code(db, update_fields["student_code"])
        if not student:
            logger.warning("Service修改就业记录失败: 学生不存在 student_code=%s", update_fields["student_code"])
            raise ValueError(f"学生编号 {update_fields['student_code']} 不存在")
        target_student_id = student.id
        update_fields["student_id"] = student.id
        del update_fields["student_code"]

    if "is_latest_employment" in update_fields:
        update_fields["is_current"] = 1 if update_fields["is_latest_employment"] else 0
        del update_fields["is_latest_employment"]

    target_company_name = update_fields.get("company_name", existing.company_name)
    target_job_open_date = update_fields.get("job_open_date", existing.job_open_date)

    duplicate = await employmentMapper.get_employment_by_unique_key(
        db, target_student_id, target_company_name, target_job_open_date
    )
    if duplicate and duplicate.id != employment_data.id:
        logger.warning("Service修改就业记录失败: 记录冲突 id=%s", employment_data.id)
        raise ValueError("修改后的就业记录与已有记录冲突")

    if update_fields.get("is_current") == 1:
        await employmentMapper.clear_current_employment(db, target_student_id, exclude_id=employment_data.id)

    await employmentMapper.update_employment(db, employment_data.id, update_fields)
    result = await employmentMapper.get_employment_detail(db, employment_data.id)
    logger.info("Service修改就业记录成功: id=%s", employment_data.id)
    return EmploymentResponse.model_validate(result)


async def delete_employment(db: AsyncSession, employment_id: int):
    logger.info("Service删除就业记录: id=%s", employment_id)
    existing = await employmentMapper.get_employment_by_id(db, employment_id)
    if not existing:
        logger.warning("Service删除就业记录失败: 记录不存在 id=%s", employment_id)
        raise ValueError(f"就业记录ID {employment_id} 不存在")

    result = await employmentMapper.delete_employment(db, employment_id)
    logger.info("Service删除就业记录成功: id=%s", employment_id)
    return result
