from sqlalchemy import MetaData, Table, Column, Float, BigInteger, Integer, String, TIMESTAMP

metadata = MetaData()

ruuvi_measurement = Table(
    'ruuvi_measurement', metadata,
    Column('time', TIMESTAMP),
    Column('mac', String),
    Column('name', String),
    Column('acceleration_x', Float),
    Column('acceleration_y', Float),
    Column('acceleration_z', Float),
    Column('battery_potential', Float),
    Column('humidity', Float),
    Column('measurement_sequence_number', BigInteger),
    Column('movement_counter', Integer),
    Column('pressure', Float),
    Column('temperature', Float),
    Column('tx_power', Integer),
    Column('move', Integer),
    Column('accelZ', Float),
    Column('epoch', TIMESTAMP),
    Column('txdbm', Integer),
    Column('accelY', Float),
    Column('sequence', BigInteger),
    Column('accelX', Float),
    Column('battery', Float)
)