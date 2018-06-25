"""empty message

Revision ID: 110a40988475
Revises: f32336cc5e99
Create Date: 2018-06-25 21:27:26.889078

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '110a40988475'
down_revision = 'f32336cc5e99'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('translation_downvoters',
    sa.Column('translation_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['translation_id'], ['translation.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('translation_id', 'user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'date_created',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('translation', 'date_created',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('term', 'date_created',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_table('translation_downvoters')
    # ### end Alembic commands ###
