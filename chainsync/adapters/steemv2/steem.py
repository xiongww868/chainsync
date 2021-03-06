from datetime import datetime

from chainsync.adapters.abstract import AbstractAdapter
from chainsync.adapters.base import BaseAdapter

from jsonrpcclient.request import Request

class SteemV2Adapter(AbstractAdapter, BaseAdapter):

    config = {
        'BLOCK_INTERVAL': 'STEEM_BLOCK_INTERVAL',
        'HEAD_BLOCK_NUMBER': 'head_block_number',
        'LAST_IRREVERSIBLE_BLOCK_NUM': 'last_irreversible_block_num',
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

    def format_op_from_get_block(self, block, op, txIndex=False, opIndex=False):
        opType, opData = op
        opData['block_num'] = block['block_num']
        opData['op_in_trx'] = opIndex
        opData['operation_type'] = opType
        opData['timestamp'] = block['timestamp']
        opData['transaction_id'] = block['transaction_ids'][txIndex]
        opData['trx_in_block'] = txIndex
        return opData

    def format_op_from_get_ops_in_block(self, op):
        opType, opData = op['op']
        opData['block_num'] = op['block']
        opData['op_in_trx'] = op['op_in_trx']
        opData['operation_type'] = opType
        opData['timestamp'] = op['timestamp']
        opData['transaction_id'] = op['trx_id']
        opData['trx_in_block'] = op['trx_in_block']
        return opData

    def format_op_from_get_transaction(self, tx, op, txIndex=False, opIndex=False):
        opType, opData = op
        opData['block_num'] = tx['block_num']
        opData['op_in_trx'] = opIndex
        opData['operation_type'] = opType
        opData['timestamp'] = False
        opData['transaction_id'] = tx['transaction_id']
        opData['trx_in_block'] = txIndex
        return opData

    def get_block(self, block_num):
        # block_api method
        api = 'block_api'
        method = 'get_block'
        # ensure the API is available
        if self.is_api_available(api, method):
            response = self.client.request('.'.join([api, method]), block_num=block_num)
            response['block']['block_num'] = int(str(response['block']['block_id'])[:8], base=16)
            return response['block']

    def get_blocks(self, blocks=[]):
        # block_api method
        api = 'block_api'
        method = 'get_block'
        if self.is_api_available(api, method):
            # assemble list with multiple requests for batch
            requests = [
                Request('.'.join([api, method]), {
                    'block_num': i
                }) for i in blocks
            ]
            # get response
            response = self.client.send(requests)
            # return the resulting block of each result
            return [dict(r['result']['block'], **{'block_num': int(str(r['result']['block']['block_id'])[:8], base=16)}) for r in response]

    def get_config(self):
        # database_api method
        api = 'database_api'
        method = 'get_config'
        if self.is_api_available(api, method):
            return self.client.request('.'.join([api, method]))

    def get_methods(self):
        # jsonrpc method
        api = 'jsonrpc'
        method = 'get_methods'
        return self.client.request('.'.join([api, method]))

    def get_ops_in_block(self, block_num, virtual_only=False):
        if self.is_api_available('account_history_api', 'get_ops_in_block', raiseException=False):
            return self.get_ops_in_block_from_account_history_api(block_num=block_num, virtual_only=virtual_only)
        elif self.is_api_available('condenser_api', 'get_ops_in_block', raiseException=False):
            return self.get_ops_in_block_from_condenser_api(block_num=block_num, virtual_only=virtual_only)
        else:
            raise Exception('endpoint not capable of calling get_ops_in_block from either condenser_api or account_history_api')

    def get_ops_in_block_from_account_history_api(self, block_num, virtual_only=False):
        # account_history_api method
        api = 'account_history_api'
        method = 'get_ops_in_block'
        response = self.client.request('.'.join([api, method]), {
            'block_num': block_num,
            'only_virtual': virtual_only
        })
        return response['ops']

    def get_ops_in_block_from_condenser_api(self, block_num, virtual_only=False):
        # condenser_api method
        api = 'condenser_api'
        method = 'get_ops_in_block'
        response = Client(self.endpoint).request('.'.join([api, method]), [
            block_num,
            virtual_only
        ])
        return response

    def get_ops_in_blocks(self, blocks, virtual_only=False):
        if self.is_api_available('account_history_api', 'get_ops_in_block', raiseException=False):
            return self.get_ops_in_blocks_from_account_history_api(blocks=blocks, virtual_only=virtual_only)
        elif self.is_api_available('condenser_api', 'get_ops_in_block', raiseException=False):
            return self.get_ops_in_blocks_from_condenser_api(blocks=blocks, virtual_only=virtual_only)
        else:
            raise Exception('endpoint not capable of calling get_ops_in_block from either condenser_api or account_history_api')

    def get_ops_in_blocks_from_account_history_api(self, blocks, virtual_only=False):
        # account_history_api method
        api = 'account_history_api'
        method = 'get_ops_in_block'
        # assemble list with multiple requests for batch
        requests = [
            Request('.'.join([api, method]), {
                'block_num': i,
                'only_virtual': virtual_only
            }) for i in blocks
        ]
        # get response
        response = self.client.send(requests)
        # return the resulting ops
        return [r['result']['ops'] for r in response]

    def get_ops_in_blocks_from_condenser_api(self, blocks, virtual_only=False):
        # condenser_api method
        api = 'condenser_api'
        method = 'get_ops_in_block'
        # assemble list with multiple requests for batch
        requests = [
            Request('.'.join([api, method]), [
                i,
                virtual_only
            ]) for i in blocks
        ]
        # get response
        response = self.client.send(requests)
        # return the resulting ops
        return [r['result'] for r in response]

    def get_status(self):
        # database_api method
        api = 'database_api'
        method = 'get_dynamic_global_properties'
        if self.is_api_available(api, method):
            return self.client.request('.'.join([api, method]))

    def get_transaction(self, transaction_id=1):
        response = self.client.request('condenser_api.get_transaction', [transaction_id])
        # try:
        #     response['block_num'] = int(str(response['block_id'])[:8], base=16)
        # except KeyError as e:
        #     print(e)
        #     print(response)
        print(response)
        # return self.call('get_transaction', transaction_id=transaction_id)

    def get_transactions(self, transaction_ids=[]):
        pass
