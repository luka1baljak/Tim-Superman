"""friends

Revision ID: 657fdabe4649
Revises: 0070d463075e
Create Date: 2019-05-06 20:54:11.270737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '657fdabe4649'
down_revision = '0070d463075e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('friends',
    sa.Column('befriender_id', sa.Integer(), nullable=True),
    sa.Column('befriended_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['befriended_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['befriender_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('friends')
    # ### end Alembic commands ###
