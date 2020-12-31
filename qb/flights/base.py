import abc


class BaseFlightSearch(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def search(self, origin, destination, departure_date, **kwargs):
		'''Search the service for tickets. The **kwargs arguments should match the provider's parameters.'''
		return

	@abc.abstractmethod
	def update(self, **kwargs):
		'''Different providers implement this differently, hence the free form arguments'''
		return
		