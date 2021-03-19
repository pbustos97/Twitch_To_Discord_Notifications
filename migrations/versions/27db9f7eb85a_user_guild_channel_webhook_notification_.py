"""user, guild, channel, webhook, notification tables

Revision ID: 27db9f7eb85a
Revises: 
Create Date: 2021-03-18 16:43:20.536997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27db9f7eb85a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('guild',
    sa.Column('guildId', sa.Integer(), nullable=False),
    sa.Column('guildName', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('guildId'),
    sa.UniqueConstraint('guildId')
    )
    op.create_table('user',
    sa.Column('discordId', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('avatarURL', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('discordId'),
    sa.UniqueConstraint('discordId')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=False)
    op.create_table('channel',
    sa.Column('channelId', sa.Integer(), nullable=False),
    sa.Column('channelName', sa.String(length=128), nullable=True),
    sa.Column('guildId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['guildId'], ['guild.guildId'], ),
    sa.PrimaryKeyConstraint('channelId'),
    sa.UniqueConstraint('channelId'),
    sa.UniqueConstraint('guildId')
    )
    op.create_table('guildUsers',
    sa.Column('guildId', sa.Integer(), nullable=True),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['guildId'], ['guild.guildId'], ),
    sa.ForeignKeyConstraint(['userId'], ['user.discordId'], )
    )
    op.create_table('webhook',
    sa.Column('webhookId', sa.Integer(), nullable=False),
    sa.Column('channelId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['channelId'], ['channel.channelId'], ),
    sa.PrimaryKeyConstraint('webhookId'),
    sa.UniqueConstraint('channelId'),
    sa.UniqueConstraint('webhookId')
    )
    op.create_table('notification',
    sa.Column('notificationId', sa.String(length=64), nullable=False),
    sa.Column('webhookId', sa.Integer(), nullable=True),
    sa.Column('twitchId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['webhookId'], ['webhook.webhookId'], ),
    sa.PrimaryKeyConstraint('notificationId'),
    sa.UniqueConstraint('twitchId'),
    sa.UniqueConstraint('webhookId')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notification')
    op.drop_table('webhook')
    op.drop_table('guildUsers')
    op.drop_table('channel')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('guild')
    # ### end Alembic commands ###
