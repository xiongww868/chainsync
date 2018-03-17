from datetime import datetime

from blocksync.adapters.abstract import AbstractAdapter
from blocksync.adapters.base import BaseAdapter
from blocksync.utils.http_client import HttpClient

from jsonrpcclient.request import Request

class SteemV2Adapter(AbstractAdapter, BaseAdapter):

    config = {
        'BLOCK_INTERVAL': 'STEEM_BLOCK_INTERVAL',
        'VIRTUAL_OPS': [
            'fill_convert_request',
            'author_reward',
            'curation_reward',
            'comment_reward',
            'liquidity_reward',
            'interest',
            'fill_vesting_withdraw',
            'fill_order',
            'shutdown_witness',
            'fill_transfer_from_savings',
            'hardfork',
            'comment_payout_update',
            'return_vesting_delegation',
            'comment_benefactor_reward',
            'producer_reward',
        ]
    }


    def opData(self, block, opType, opData, txIndex=False):
        # Ensure the format of the timestamp as a datetime
        if not isinstance(block['timestamp'], datetime):
            opData['timestamp'] = datetime.strptime(block['timestamp'], '%Y-%m-%dT%H:%M:%S')
        else:
            opData['timestamp'] = block['timestamp']
        # Add some useful context to the operation
        opData['block_num'] = block['block_num']
        opData['operation_type'] = opType
        opData['transaction_id'] = block['transaction_ids'][txIndex]
        return opData

    def vOpData(self, vop):
        # Extract the operation from the vop object
        opType, opData = vop['op']
        # Ensure the format of the timestamp as a datetime
        if not isinstance(vop['timestamp'], datetime):
            opData['timestamp'] = datetime.strptime(vop['timestamp'], '%Y-%m-%dT%H:%M:%S')
        else:
            opData['timestamp'] = vop['timestamp']
        # Add some useful context to the operation
        opData['block_num'] = vop['block']
        opData['operation_type'] = opType
        opData['transaction_id'] = vop['trx_id']
        return opData

    def get_block(self, block_num):
        response = HttpClient(self.endpoint).request('block_api.get_block', block_num=block_num)
        response['block']['block_num'] = int(str(response['block']['block_id'])[:8], base=16)
        return response['block']

    def get_ops_in_block(self, block_num, virtual_only=False):
        return HttpClient(self.endpoint).request('condenser_api.get_ops_in_block', [block_num, virtual_only])

    def get_ops_in_blocks(self, start_block=1, virtual_only=False, blocks=10):
        requests = [Request('condenser_api.get_ops_in_block', [i, virtual_only]) for i in range(start_block, start_block + blocks)]
        response = HttpClient(self.endpoint).send(requests)
        return [r['result'] for r in response]

    def get_blocks(self, start_block=1, blocks=10):
        requests = [Request('block_api.get_block', block_num=i) for i in range(start_block, start_block + blocks)]
        response = HttpClient(self.endpoint).send(requests)
        return [dict(r['result']['block'], **{'block_num': int(str(r['result']['block']['block_id'])[:8], base=16)}) for r in response]

    def get_config(self):
        return HttpClient(self.endpoint).request('database_api.get_config')

    def get_methods(self):
        return HttpClient(self.endpoint).request('get_methods')

    def get_status(self):
        return HttpClient(self.endpoint).request('database_api.get_dynamic_global_properties')
