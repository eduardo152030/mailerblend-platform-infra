"""Apply signed partition grants to expense reads and writes."""
from asyncpg import Connection
from fastapi import Depends, HTTPException, Request

from app.core.crm_access import CRMAccess, bearer, crm_auth_enabled, require_crm_access
from app.db import get_db


def expense_access(request: Request, credentials=Depends(bearer)) -> CRMAccess | None:
    if not crm_auth_enabled():
        return None
    access = require_crm_access(credentials)
    write = request.method not in {"GET", "HEAD"}
    if not access.expense_partitions(write=write):
        raise HTTPException(403, "Expense access forbidden")
    partition = request.query_params.get("project_key")
    if partition:
        access.require_expense_partition(partition, write=write)
    return access


class ExpenseReads:
    def __init__(self, conn: Connection, access: CRMAccess | None):
        self.conn = conn
        self.partitions = None if access is None or access.is_admin else sorted(access.expense_partitions())

    def query(self, sql: str, args: tuple) -> tuple:
        # The CTE scopes the gastos relation in lists, aggregations and exports.
        if self.partitions is None:
            return sql, args
        scope = f"gastos AS (SELECT * FROM public.gastos WHERE project_key = ANY(${len(args) + 1}::text[]))"
        statement = sql.strip()
        if statement.startswith("WITH "):
            statement = f"WITH {scope}, {statement[5:]}"
        else:
            statement = f"WITH {scope} {statement}"
        return statement, (*args, self.partitions)

    async def fetch(self, sql, *args):
        statement, bound = self.query(sql, args)
        return await self.conn.fetch(statement, *bound)

    async def fetchrow(self, sql, *args):
        statement, bound = self.query(sql, args)
        return await self.conn.fetchrow(statement, *bound)

    async def fetchval(self, sql, *args):
        statement, bound = self.query(sql, args)
        return await self.conn.fetchval(statement, *bound)


async def expense_reads(conn: Connection = Depends(get_db), access: CRMAccess | None = Depends(expense_access)) -> ExpenseReads:
    return ExpenseReads(conn, access)
