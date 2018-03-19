import datetime
from blocksync import Blocksync
from blocksync.adapters.steemv2 import SteemV2Adapter

adapter = SteemV2Adapter(endpoints=['https://api.steemitstage.com/'])

blocksync = Blocksync(adapter)

print('\nGetting block 1')
block = blocksync.get_block(1)
print(block)

print('\nGetting blocks 1, 10, 50, 250, 500')
blocks = blocksync.get_blocks([1, 10, 50, 250, 500])
for block in blocks:
    print(block)

print('\nGetting blocks 1000-1005')
blocks = blocksync.get_block_sequence(1000, 5)
for block in blocks:
    print(block)

print('\nStreaming all blocks...')
for block in blocksync.get_block_stream():
    print("{}: {} - {}".format(datetime.datetime.now(), block['block_num'], block['witness']))

print('\nStreaming all ops...')
for op in blocksync.get_op_stream():
    print("{}: {} [{}] - {}".format(datetime.datetime.now(), op['block_num'], op['transaction_id'], op['operation_type']))

print('\nStreaming all non-virtual ops...')
for op in blocksync.get_op_stream(virtual_ops=False):
    print("{}: {} [{}] - {}".format(datetime.datetime.now(), op['block_num'], op['transaction_id'], op['operation_type']))

print('\nStreaming all virtual ops...')
for op in blocksync.get_op_stream(virtual_only=True):
    print("{}: {} [{}] - {}".format(datetime.datetime.now(), op['block_num'], op['transaction_id'], op['operation_type']))

print('\nStreaming vote ops only...')
for op in blocksync.get_op_stream(whitelist=['vote']):
    print("{}: {} - {} by {}".format(datetime.datetime.now(), op['block_num'], op['operation_type'], op['voter']))

print('\nStreaming producer_reward virtual ops only...')
for op in blocksync.get_op_stream(whitelist=['producer_reward']):
    print("{}: {} - {} for {} of {}".format(datetime.datetime.now(), op['block_num'], op['operation_type'], op['producer'], op['vesting_shares']))

print('\nStreaming all blocks + ops + virtual ops...')
for dataType, data in blocksync.get_blockop_stream():
    dataHeader = "{}: {}".format(datetime.datetime.now(), dataType)
    if dataType == "op":
        print("{} {} {}".format(dataHeader, data['transaction_id'], data['operation_type']))
    if dataType == "block":
        txCount = len(data['transactions'])
        opCount = sum([len(tx['operations']) for tx in data['transactions']])
        print("{} - tx: {} / ops: {}".format(dataHeader, txCount, opCount))

print('\nStreaming all blocks + ops (no virtual ops)...')
for dataType, data in blocksync.get_blockop_stream(virtual_ops=False):
    dataHeader = "{}: {}".format(datetime.datetime.now(), dataType)
    if dataType == "op":
        print("{} {} {}".format(dataHeader, data['transaction_id'], data['operation_type']))
    if dataType == "block":
        txCount = len(data['transactions'])
        opCount = sum([len(tx['operations']) for tx in data['transactions']])
        print("{} - tx: {} / ops: {}".format(dataHeader, txCount, opCount))

print('\nStreaming all blocks + ops (no virtual ops), filtering only votes...')
for dataType, data in blocksync.get_blockop_stream(virtual_ops=False, whitelist=['vote']):
    dataHeader = "{}: {}".format(datetime.datetime.now(), dataType)
    if dataType == "op":
        print("{} {} {}".format(dataHeader, data['transaction_id'], data['operation_type']))
    if dataType == "block":
        txCount = len(data['transactions'])
        opCount = sum([len(tx['operations']) for tx in data['transactions']])
        print("{} - tx: {} / ops: {}".format(dataHeader, txCount, opCount))

print('\nStreaming all blocks + virtual ops (no normal ops)...')
for dataType, data in blocksync.get_blockop_stream(virtual_only=True):
    dataHeader = "{}: {}".format(datetime.datetime.now(), dataType)
    if dataType == "op":
        print("{} {} {}".format(dataHeader, data['transaction_id'], data['operation_type']))
    if dataType == "block":
        txCount = len(data['transactions'])
        opCount = sum([len(tx['operations']) for tx in data['transactions']])
        print("{} - tx: {} / ops: {}".format(dataHeader, txCount, opCount))

print('\nStreaming all blocks + virtual ops (no normal ops), filtering only producer_reward...')
for dataType, data in blocksync.get_blockop_stream(virtual_only=True, whitelist=['producer_reward']):
    dataHeader = "{}: {}".format(datetime.datetime.now(), dataType)
    if dataType == "op":
        print("{} {} {}".format(dataHeader, data['transaction_id'], data['operation_type']))
    if dataType == "block":
        txCount = len(data['transactions'])
        opCount = sum([len(tx['operations']) for tx in data['transactions']])
        print("{} - tx: {} / ops: {}".format(dataHeader, txCount, opCount))
