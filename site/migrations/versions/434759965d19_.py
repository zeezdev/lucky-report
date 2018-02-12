"""empty message

Revision ID: 434759965d19
Revises: 
Create Date: 2018-02-12 00:13:05.496094

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '434759965d19'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('requests',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('request', sa.Text(), nullable=True),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('session', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('requests')
    # ### end Alembic commands ###
