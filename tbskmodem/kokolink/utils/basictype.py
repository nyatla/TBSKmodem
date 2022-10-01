# import itertools
# from typing import Generic,TypeVar

# from abc import ABC



# from ..interfaces import IRoStream,IFilter,IByteStream


# T=TypeVar("T")
# class BasicRoStream(IRoStream[T],Generic[T],ABC):
#     """IRoStreamの基本実装です。
#     get/posメソッドを実装することで機能します。Seek,getsはgetをラップしてエミュレートします。
#     getメソッドの中でself#_posを更新してください。
#     """
#     def gets(self,maxsize:int):
#         return tuple(itertools.islice(self,maxsize))
#     def seek(self,size:int):
#         if len(self.gets(size))<size:
#             raise StopIteration()


# class BasicByteStream(BasicRoStream[int],IByteStream,ABC):
#     def getAsUInt32be(self)->int:
#         """BigEndianのUint32を読み出す
#         """
#         r=0
#         for i in self.gets(4):
#             r=r<<8|i
#         return r
#     def getAsByteArray(self,maxsize)->bytearray:
#         """gets関数をラップします。
#         """
#         r=bytearray()
#         # print(self.gets(maxsize))
#         # return struct.pack("B",self.gets(maxsize))
#         for i in self.gets(maxsize):
#             r.append(i)
#         return r




# S=TypeVar("S")
# D=TypeVar("D")
# class BasicFilter(IFilter[S,D],Generic[S,D],ABC):
#     """IFilterの基本実装です。
#     doFilterを実装することで機能します。
#     """
#     def __call__(self,src:S)->D:
#         return self.doFilter(src)


