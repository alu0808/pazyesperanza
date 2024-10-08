"""Crear cambios0710-6

Revision ID: 18abf5427d2e
Revises: 0b0713e0fd4f
Create Date: 2024-10-07 20:15:01.377382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18abf5427d2e'
down_revision = '0b0713e0fd4f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('avance_politica_memoria', schema=None) as batch_op:
        batch_op.alter_column('nombre_politica_memoria',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=200),
               existing_nullable=False)
        batch_op.alter_column('ocurrencias_periodo',
               existing_type=sa.TEXT(),
               type_=sa.String(length=400),
               existing_nullable=True)
        batch_op.alter_column('actividades_realizadas',
               existing_type=sa.TEXT(),
               type_=sa.String(length=400),
               existing_nullable=True)
        batch_op.alter_column('estado_actual_gestion',
               existing_type=sa.TEXT(),
               type_=sa.String(length=400),
               existing_nullable=True)
        batch_op.alter_column('recomendaciones',
               existing_type=sa.TEXT(),
               type_=sa.String(length=350),
               existing_nullable=True)
        batch_op.alter_column('otro_asunto',
               existing_type=sa.TEXT(),
               type_=sa.String(length=255),
               existing_nullable=True)
        batch_op.alter_column('responsable_registro',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=100),
               existing_nullable=True)

    with op.batch_alter_table('politica_nacional_memoria', schema=None) as batch_op:
        batch_op.alter_column('nombre_politica_memoria',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=200),
               existing_nullable=False)
        batch_op.alter_column('localizacion',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=200),
               existing_nullable=True)
        batch_op.alter_column('descripcion_propuesta',
               existing_type=sa.TEXT(),
               type_=sa.String(length=300),
               existing_nullable=True)
        batch_op.alter_column('institucion_1',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=200),
               existing_nullable=True)
        batch_op.alter_column('institucion_2',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=200),
               existing_nullable=True)
        batch_op.alter_column('institucion_3',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=200),
               existing_nullable=True)
        batch_op.alter_column('organizaciones_aliadas',
               existing_type=sa.TEXT(),
               type_=sa.String(length=300),
               existing_nullable=True)
        batch_op.alter_column('otro_dato',
               existing_type=sa.TEXT(),
               type_=sa.String(length=255),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('politica_nacional_memoria', schema=None) as batch_op:
        batch_op.alter_column('otro_dato',
               existing_type=sa.String(length=255),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('organizaciones_aliadas',
               existing_type=sa.String(length=300),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('institucion_3',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('institucion_2',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('institucion_1',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('descripcion_propuesta',
               existing_type=sa.String(length=300),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('localizacion',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('nombre_politica_memoria',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)

    with op.batch_alter_table('avance_politica_memoria', schema=None) as batch_op:
        batch_op.alter_column('responsable_registro',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('otro_asunto',
               existing_type=sa.String(length=255),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('recomendaciones',
               existing_type=sa.String(length=350),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('estado_actual_gestion',
               existing_type=sa.String(length=400),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('actividades_realizadas',
               existing_type=sa.String(length=400),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('ocurrencias_periodo',
               existing_type=sa.String(length=400),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('nombre_politica_memoria',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###
