"""add id for users_scopes, add constraints

Revision ID: 4eb622800706
Revises: 86a440250d30
Create Date: 2022-01-07 15:27:49.046968

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4eb622800706'
down_revision = '86a440250d30'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'conversations_users', ['conversation_id', 'user_id'])
    op.add_column('users_scopes', sa.Column('id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'users_scopes', ['user_id', 'scope_name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users_scopes', type_='unique')
    op.drop_column('users_scopes', 'id')
    op.drop_constraint(None, 'conversations_users', type_='unique')
    # ### end Alembic commands ###
