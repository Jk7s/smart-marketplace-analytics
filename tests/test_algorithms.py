import unittest
from algorithms import search_products, keyword_score, percentile, shard_replica_experiment

PRODUCTS = [
 {"id":1,"title":"Lightweight Laptop","description":"Laptop for programming","category":"Electronics/Computers","price":50000,"stock":4},
 {"id":2,"title":"Gaming Laptop","description":"Powerful computer","category":"Electronics/Computers","price":75000,"stock":2},
 {"id":3,"title":"Laptop Case","description":"Protective laptop bag","category":"Fashion/Bags","price":1000,"stock":0},
]
class AlgorithmTests(unittest.TestCase):
    def test_price_and_stock_filters(self):
        result=search_products(PRODUCTS,"laptop",60000,"All",True,"Keyword",10)
        self.assertEqual([x["id"] for x in result],[1])
    def test_category_path_filter(self):
        result=search_products(PRODUCTS,"laptop",80000,"Electronics",False,"Hybrid",10)
        self.assertEqual({x["id"] for x in result},{1,2})
    def test_percentile(self):
        self.assertEqual(percentile([1,2,3,4,5],50),3.0)
    def test_shards_cover_all_records(self):
        result=shard_replica_experiment(PRODUCTS,2)
        self.assertEqual(sum(x["primary_records"] for x in result),3)
    def test_keyword_score(self):
        self.assertGreater(keyword_score("programming",PRODUCTS[0]),0)
if __name__=="__main__": unittest.main()
