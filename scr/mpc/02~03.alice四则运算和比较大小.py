import secretflow as sf
from scr.utils import *

# Check the version of your SecretFlow
print("The version of SecretFlow: {}".format(sf.__version__))

# In case you have a running secretflow runtime already.
sf.shutdown()

alice, bob = sf_init_cluster()
print("Alice and Bob are ready to go!")

spu_device = spu_init_cluster()
print("*********************Alice SPU")


alice_data_pyu = device_get_data(alice, 11)
alice_data_spu = alice_data_pyu.to(spu_device)
bob_data_pyu = device_get_data(bob, 44)
bob_data_spu = bob_data_pyu.to(spu_device)


print("数据读取完成")
# 四则运算
def apply_operator(a, b):
    return a + b, a - b, a * b, a / b


# 比较大小
def bigger(a, b):
    return a > b


alice_bigger_bob_data = spu_device(bigger)(alice_data_spu, bob_data_spu)
alice_add_bob_data = spu_device(apply_operator)(alice_data_spu, bob_data_spu)

print("计算完成")
print(sf.reveal(alice_add_bob_data))
print(sf.reveal(alice_bigger_bob_data))

print("*****************************************************只有Alice得到数据")
alice_add_bob_alice_pyu = alice_add_bob_data.to(alice)
alice.dump(
    alice_add_bob_alice_pyu,
    "/mnt/users/beng003/sf-test/sf/data/alice/alice_add_bob_data.txt",
)

sf.shutdown()
