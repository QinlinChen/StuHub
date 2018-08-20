"""empty message

Revision ID: 73047ad7e434
Revises: d4695d446ed0
Create Date: 2018-08-19 22:17:33.319979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73047ad7e434'
down_revision = 'd4695d446ed0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('body_html', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'body_html')
    # ### end Alembic commands ###
