# from mms_client.client import MmsClient
# from mms_client.security.certs import Certificate
# from mms_client.utils.web import ClientType
# from mms_client.types.reserve import ReserveRequirementQuery
# from mms_client.types.market import MarketType
# from mms_client.types.enums import AreaCode
# from pathlib import Path
# from pendulum import Date

# # Create a certificate
# cert = Certificate(Path("/mnt/c/Users/RyanWood/Downloads/EndUser.p12"), "XEEx9CEc")

# # Create a new MMS client
# client = MmsClient("electroroute.co.jp", "D072", "ERJVPP005", ClientType.BSP, cert)

# # Create a query for reserve requirements
# query = ReserveRequirementQuery(market_type=MarketType.DAY_AHEAD, area=AreaCode.TOKYO)

# # Submit the query to the MMS and get the results
# try:
#     resp = client.query_reserve_requirements(query, days=1, date=Date(2024, 7, 18))

#     # Print out the results
#     print(resp)
# except Exception as e:
#     print(e)
