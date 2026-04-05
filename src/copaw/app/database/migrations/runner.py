"""
数据库迁移工具

执行 SQL 迁移脚本
"""

import os
from pathlib import Path
from typing import List
from sqlalchemy import text
from .connection import get_engine, session_scope


class MigrationRunner:
    """
    迁移执行器
    
    按顺序执行 SQL 迁移脚本
    """
    
    def __init__(self, migrations_dir: str = None):
        """
        Args:
            migrations_dir: 迁移脚本目录（默认：当前目录下的 migrations）
        """
        if migrations_dir is None:
            migrations_dir = Path(__file__).parent / "migrations"
        
        self.migrations_dir = Path(migrations_dir)
    
    def get_pending_migrations(self) -> List[str]:
        """
        获取待执行的迁移脚本
        
        Returns:
            迁移脚本文件名列表（已排序）
        """
        if not self.migrations_dir.exists():
            return []
        
        # 获取所有 SQL 文件
        sql_files = sorted([
            f.name for f in self.migrations_dir.iterdir()
            if f.suffix == ".sql"
        ])
        
        # TODO: 查询已执行的迁移，过滤掉已执行的
        # 这里简化处理，返回所有文件
        return sql_files
    
    def run_migration(self, migration_file: str) -> bool:
        """
        执行单个迁移脚本
        
        Args:
            migration_file: 迁移脚本文件名
        
        Returns:
            是否成功
        """
        migration_path = self.migrations_dir / migration_file
        
        if not migration_path.exists():
            print(f"❌ Migration file not found: {migration_path}")
            return False
        
        print(f"🔄 Running migration: {migration_file}")
        
        try:
            with session_scope() as session:
                # 读取 SQL 文件
                sql_content = migration_path.read_text(encoding="utf-8")
                
                # 执行 SQL（支持多条语句）
                for statement in sql_content.split(";"):
                    statement = statement.strip()
                    if statement:
                        session.execute(text(statement))
                
                print(f"✅ Migration completed: {migration_file}")
                return True
        
        except Exception as e:
            print(f"❌ Migration failed: {migration_file}")
            print(f"   Error: {e}")
            return False
    
    def run_all(self) -> bool:
        """
        执行所有待执行的迁移
        
        Returns:
            是否全部成功
        """
        migrations = self.get_pending_migrations()
        
        if not migrations:
            print("✓ No pending migrations")
            return True
        
        print(f"📋 Found {len(migrations)} migration(s)")
        
        success_count = 0
        for migration in migrations:
            if self.run_migration(migration):
                success_count += 1
            else:
                print(f"⚠️  Stopping due to error")
                break
        
        print(f"\n{'='*60}")
        print(f"Migration summary: {success_count}/{len(migrations)} successful")
        print(f"{'='*60}")
        
        return success_count == len(migrations)


def run_migrations():
    """运行所有迁移（快捷函数）"""
    runner = MigrationRunner()
    return runner.run_all()


if __name__ == "__main__":
    # 初始化数据库
    from .connection import init_database
    init_database("sqlite:///copaw.db", echo=False)
    
    # 运行迁移
    run_migrations()
