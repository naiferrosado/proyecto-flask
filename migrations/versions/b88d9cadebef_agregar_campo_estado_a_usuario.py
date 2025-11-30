from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b88d9cadebef'
down_revision = '4f87a47f0e53'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Agregar columna PERMITIENDO NULL
    with op.batch_alter_table('usuario') as batch_op:
        batch_op.add_column(sa.Column('estado', sa.String(length=20), nullable=True))

    # 2. Asignar valor a los usuarios existentes
    op.execute("UPDATE usuario SET estado = 'activo' WHERE estado IS NULL;")

    # 3. Cambiar la columna a NOT NULL
    with op.batch_alter_table('usuario') as batch_op:
        batch_op.alter_column('estado', nullable=False)


def downgrade():
    with op.batch_alter_table('usuario') as batch_op:
        batch_op.drop_column('estado')
