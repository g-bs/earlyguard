# blockchain.py
import hashlib
import json
from datetime import datetime
from pathlib import Path

class SimpleBlockchain:
    def __init__(self, chain_file="data/blockchain.json"):
        self.chain_file = Path(chain_file)
        self.chain = []
        self.load_chain()

    def create_block(self, data, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.utcnow()),
            "data": data,
            "previous_hash": previous_hash,
        }
        block["hash"] = self.hash(block)
        self.chain.append(block)
        self.save_chain()
        return block

    def get_last_block(self):
        return self.chain[-1] if self.chain else self.create_genesis_block()

    def create_genesis_block(self):
        genesis_data = {"info": "Genesis Block"}
        return self.create_block(genesis_data, "0")

    def hash(self, block):
        encoded = json.dumps({k: block[k] for k in block if k != "hash"}, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    def load_chain(self):
        if self.chain_file.exists():
            try:
                with open(self.chain_file, "r") as f:
                    self.chain = json.load(f)
            except json.JSONDecodeError:
                self.chain = []
        if not self.chain:
            self.create_genesis_block()

    def save_chain(self):
        self.chain_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.chain_file, "w") as f:
            json.dump(self.chain, f, indent=4)

    def get_chain(self):
        return self.chain
