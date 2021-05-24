### Exception classes

class Error(Exception):
	pass

class ArgumentMissing(Error):
	pass

class CommandUnknown(Error):
	pass

class ResourceNotConfigured(Error):
	pass

class FunctionalityNotImplemented(Error):
	pass

class ResponseInvalid(Error):
	pass

class ProviderNotConfigured(Error):
	pass