"""initial db

Revision ID: 39090c2ff4d6
Revises: 
Create Date: 2021-03-30 14:40:08.249869

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39090c2ff4d6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('guild',
    sa.Column('guildId', sa.Integer(), nullable=False),
    sa.Column('guildName', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('guildId'),
    sa.UniqueConstraint('guildId')
    )
    op.create_table('user',
    sa.Column('discordId', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('discriminator', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('avatarURL', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('discordId'),
    sa.UniqueConstraint('discordId')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=False)
    op.create_table('channel',
    sa.Column('channelId', sa.Integer(), nullable=False),
    sa.Column('channelName', sa.String(), nullable=True),
    sa.Column('guildId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['guildId'], ['guild.guildId'], ),
    sa.PrimaryKeyConstraint('channelId'),
    sa.UniqueConstraint('channelId')
    )
    op.create_table('guildUserLink',
    sa.Column('guildId', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['guildId'], ['guild.guildId'], ),
    sa.ForeignKeyConstraint(['userId'], ['user.discordId'], ),
    sa.PrimaryKeyConstraint('guildId', 'userId')
    )
    op.create_table('webhook',
    sa.Column('webhookId', sa.Integer(), nullable=False),
    sa.Column('channelId', sa.Integer(), nullable=True),
    sa.Column('webhookURL', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['channelId'], ['channel.channelId'], ),
    sa.PrimaryKeyConstraint('webhookId'),
    sa.UniqueConstraint('webhookId'),
    sa.UniqueConstraint('webhookURL')
    )
    op.create_table('notification',
    sa.Column('notificationId', sa.String(), nullable=False),
    sa.Column('webhookId', sa.Integer(), nullable=True),
    sa.Column('twitchId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['webhookId'], ['webhook.webhookId'], ),
    sa.PrimaryKeyConstraint('notificationId'),
    sa.UniqueConstraint('notificationId'),
    sa.UniqueConstraint('twitchId')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notification')
    op.drop_table('webhook')
    op.drop_table('guildUserLink')
    op.drop_table('channel')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('guild')
    # ### end Alembic commands ###
