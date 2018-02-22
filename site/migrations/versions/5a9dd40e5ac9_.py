"""empty message

Revision ID: 5a9dd40e5ac9
Revises: daae827918ee
Create Date: 2018-02-20 14:47:02.635402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a9dd40e5ac9'
down_revision = 'daae827918ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('foreign_keys_column_id_foreign_column_id_key', 'foreign_keys', type_='unique')
    op.create_unique_constraint(None, 'foreign_keys', ['name', 'column_id', 'foreign_column_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'foreign_keys', type_='unique')
    op.create_unique_constraint('foreign_keys_column_id_foreign_column_id_key', 'foreign_keys', ['column_id', 'foreign_column_id'])
    # ### end Alembic commands ###
