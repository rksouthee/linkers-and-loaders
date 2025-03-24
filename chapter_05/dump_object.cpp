#include <cassert>
#include <iostream>
#include <fstream>
#include <vector>
#include <iterator>
#include <string_view>
#include <span>
#include <iomanip>

namespace coff
{
#pragma pack(push, 1)
struct File_header
{
	std::uint16_t magic_number;
	std::uint16_t number_of_sections;
	std::int32_t  timestamp;
	std::int32_t symbol_table_ptr;
	std::int32_t number_of_symbols;
	std::uint16_t size_of_optional_header;
	std::uint16_t flags;
};
static_assert(sizeof(File_header) == 20);

struct Section_header
{
	char name[8];
	std::int32_t physical_address;
	std::int32_t virtual_address;
	std::int32_t size_in_bytes;
	std::int32_t data_offset;
	std::int32_t relocation_offset;
	std::int32_t line_number_offset;
	std::uint16_t number_of_relocations;
	std::uint16_t number_of_line_numbers;
	std::int32_t flags;
};
static_assert(sizeof(Section_header) == 40);

struct Symbol
{
	char name[8];
	std::int32_t value;
	std::int16_t section_number;
	std::uint16_t type;
	unsigned char storage_class;
	unsigned char number_of_aux_symbols;
};
static_assert(sizeof(Symbol) == 18);

struct Symbol_record
{
	std::uint16_t length;
	std::uint16_t type;
};

struct Object_name
{
	std::uint32_t signature;
	char path[0];
};

struct Compiler_options
{
	struct {
		unsigned long language			: 8; // language index
		unsigned long edit_and_continue		: 1; // compiled for edit and continue
		unsigned long no_debug_info		: 1; // not compiled with debug info
		unsigned long ltcg			: 1; // compiled with LTCG
		unsigned long no_data_align		: 1; // compiled with /bzalign
		unsigned long managed_code_present	: 1; // managed code/data present
		unsigned long security_checks		: 1; // compiled with /GS
		unsigned long hot_patch			: 1; // compiled with /hotpatch
		unsigned long cvtcil			: 1; // converted by CVTCIL
		unsigned long msil_module		: 1; // MSIL module
		unsigned long sdl			: 1; // commpiled with /sdl
		unsigned long pgo 			: 1; // compiled with pgo
		unsigned long exp 			: 1; // .EXP module
	} flags;
	std::uint16_t machine; // target processor
	std::uint16_t frontend_version_major;
	std::uint16_t frontend_version_minor;
	std::uint16_t frontend_version_build;
	std::uint16_t frontend_version_qfe;
	std::uint16_t backend_version_major;
	std::uint16_t backend_version_minor;
	std::uint16_t backend_version_build;
	std::uint16_t backend_version_qfe;
	char version_string[0]; // null-terminated string
};

#pragma pack(pop)
}

namespace code_view
{
	struct Modifier_attribute
	{
		std::uint16_t const_ : 1;
		std::uint16_t volatile_ : 1;
		std::uint16_t unaligned : 1;
		std::uint16_t unused : 13;
	};

#pragma pack(push, 1)
	struct Modifier
	{
		std::uint16_t leaf;
		std::uint32_t type;
		std::uint16_t attributes;
	};

	struct Pointer
	{
		std::uint16_t leaf;
		std::uint32_t type;
		std::uint32_t ptr_type : 5;
		std::uint32_t ptr_mode : 3;
		std::uint32_t is_flat32 : 1;
		std::uint32_t is_volatile : 1;
		std::uint32_t is_const : 1;
		std::uint32_t is_aligned : 1;
		std::uint32_t is_restrict : 1;
		std::uint32_t size : 6;
		std::uint32_t is_mocom : 1;
		std::uint32_t is_lref : 1;
		std::uint32_t is_rref : 1;
		std::uint32_t unused : 10;
	};
#pragma pack(pop)

	struct Properties
	{
		std::uint16_t package : 1; // true if structure is packed
		std::uint16_t ctor : 1; // true if constructors or destructors present
		std::uint16_t overloaded_ops : 1; // true if overloaed operators present
		std::uint16_t is_nested : 1; // true if this is a nested type
		std::uint16_t has_nested : 1; // true if this class contains nested types
		std::uint16_t is_assignment_overloaded : 1; // true if overloaded assignment (=)
		std::uint16_t has_casting_methods : 1; // true if casting methods
		std::uint16_t is_forward_reference : 1; // true if this is a forward reference (incomplete definition)
		std::uint16_t scoped : 1; // scoped definition
		std::uint16_t has_unique_name : 1; // true if there is a decorated name following the regular name
		std::uint16_t sealed : 1; // true if class cannot be used as a base class
		std::uint16_t hfa : 2; // CV_HFA_e
		std::uint16_t intrinsic : 1; // true if class is an intrinsic type (e.g. __m128d)
		std::uint16_t mocom : 2; // CV_MOCOM_UDT_e
	};

	struct Structure
	{
		std::uint16_t leaf;
		std::uint16_t count; // count of number of elements in structure
		Properties properties; // property attribute field
		std::uint32_t field; // type index of LF_FIELD descriptor list
		std::uint32_t derived; // type index of derived from list if not zero
		std::uint32_t vshape; // type index of vshape table for this class
				      // The name of the structure follows as a null-terminated string
				      // If properties.has_unique_name is true, the unique name follows as a null-terminated string
	};

	struct Member_attributes
	{
		std::uint16_t access: 2; // access protection CV_access_t
		std::uint16_t method_properties: 3; // method properties CV_methodprop_t
		std::uint16_t pseudo: 1; // compiler generated fcn and does not exist
		std::uint16_t no_inherit: 1; // true if class cannot be inherited
		std::uint16_t no_construct: 1; // true if class cannot be constructed
		std::uint16_t comp_gen_x: 1; // compiler generated fcn and does exist
		std::uint16_t sealed: 1; // true if method cannot be overriden
		std::uint16_t unused: 6; // unused
	};

#pragma pack(push, 1)
	struct Member
	{
		std::uint16_t kind;
		Member_attributes attributes;
		std::uint32_t index; // index of type record
		std::uint16_t offset;
	};

	struct String_id
	{
		std::uint16_t kind;
		std::uint32_t id;
		// name null terminated
	};

	struct Udt_src_line
	{
		std::uint16_t kind; // LF_UDT_SRC_LINE
		std::uint32_t type; // UDT's type index
		std::uint32_t source; // Index to LF_STRING_ID record where source file name is saved
		std::uint32_t line_number;
	};

	struct Build_info
	{
		std::uint16_t kind; // LF_BUILDINFO
		std::uint16_t count; // number of arguments
		// arguments as CodeItemId
	};

	struct Func_id
	{
		std::uint16_t kind; // LF_FUNC_ID
		std::uint32_t scope_id; // parent scope of the ID, 0 if global
		std::uint32_t type; // function type
		// name - null-terminated
	};

	struct Procedure
	{
		std::uint16_t kind; // LF_PROCEDURE
		std::uint32_t return_type; // type index of return value
		std::uint8_t calling_convention; // calling convention (CV_call_t)
		std::uint8_t attributes; // CV_funcattr_t
		std::uint16_t parameter_count;
		std::uint32_t arg_list; // type index of argument list
	};

	struct Argument_list
	{
		std::uint16_t kind; // LF_ARGLIST
		std::uint32_t count; // number of arguments
		// list of type indices (of length `count`)
	};
#pragma pack(pop)
}

template <typename T>
std::pair<const T*, std::span<const std::uint8_t>> parse(std::span<const std::uint8_t> bytes)
{
	assert(bytes.size() >= sizeof(T));
	const T* ptr = reinterpret_cast<const T*>(bytes.data());
	bytes = bytes.subspan(sizeof(T));
	return { ptr, bytes };
}

std::pair<std::string_view, std::span<const std::uint8_t>> parse_string(std::span<const std::uint8_t> bytes)
{
	auto iter = std::find(bytes.begin(), bytes.end(), '\0');
	assert(iter != bytes.end());
	const std::string_view sv(reinterpret_cast<const char*>(bytes.data()), iter - bytes.begin());
	++iter;
	bytes = bytes.subspan(iter - bytes.begin());
	return { sv, bytes };
}

std::string_view get_name(const char* name, const std::string_view string_table)
{
	if (name[0] == 0 && name[1] == 0 && name[2] == 0 && name[3] == 0)
	{
		const std::int32_t offset = *reinterpret_cast<const std::int32_t*>(name + 4) - 4;
		assert(offset < string_table.size());
		const auto start = string_table.begin() + offset;
		const auto end = std::find(start, string_table.end(), '\0');
		return { start, end };
	}

	// Check if this is used!
	if (name[0] == '/')
	{
		std::uint32_t offset = 0;
		for (int i = 1; i < 8; ++i)
		{
			// Should check this is a decimal character!
			offset = offset * 10 + name[i];
		}
		const auto start = string_table.begin() + offset;
		const auto end = std::find(start, string_table.end(), '\0');
		return { start, end };
	}
	const auto end = std::find(name, name + 8, '\0');
	return { name, end };
}

void dump_symbol(const coff::Symbol_record* record, std::span<const unsigned char> data)
{
	switch (record->type)
	{
	case 0x1101: // S_OBJNAME - path to the object file name
		{
			assert(data.size() >= sizeof(coff::Object_name));
			const auto object_name = reinterpret_cast<const coff::Object_name*>(data.data());
			std::cout << "S_OBJNAME: Signature: " << object_name->signature << ", " << object_name->path << '\n';
		}
		break;

	case 0x113c: // S_COMPILE3 - compiler flags
		{
			const char* options[2] = { "no", "yes" };
			assert(data.size() >= sizeof(coff::Compiler_options));
			const auto compiler_options = reinterpret_cast<const coff::Compiler_options*>(data.data());
			std::cout << "S_COMPILE3:\n";
			std::cout << "\tLanguage: " << compiler_options->flags.language << '\n';
			std::cout << "\tTarget processor: " << compiler_options->machine << '\n';
			std::cout << "\tCompiled for edit and continue: " << options[compiler_options->flags.edit_and_continue] << '\n';
			std::cout << "\tCompiled without debugging information: " << options[compiler_options->flags.no_debug_info] << '\n';
			std::cout << "\tCompiled with LTCG: " << options[compiler_options->flags.ltcg] << '\n';
			std::cout << "\tCompiler with /bzalign: " << options[compiler_options->flags.no_data_align] << '\n';
			std::cout << "\tManaged code present: " << options[compiler_options->flags.managed_code_present] << '\n';
			std::cout << "\tCompiled with /GS: " << options[compiler_options->flags.security_checks] << '\n';
			std::cout << "\tCompiled with /hotpatch: " << options[compiler_options->flags.hot_patch] << '\n';
			std::cout << "\tConverted by CVTCIL: " << options[compiler_options->flags.cvtcil] << '\n';
			std::cout << "\tMSIL module: " << options[compiler_options->flags.msil_module] << '\n';
			std::cout << "\tCompiled with /sdl: " << options[compiler_options->flags.sdl] << '\n';
			std::cout << "\tCompiled with pgo: " << options[compiler_options->flags.pgo] << '\n';
			std::cout << "\t.EXP module: " << options[compiler_options->flags.exp] << '\n';
			std::cout << "\tFrontend Version: Major = " << compiler_options->frontend_version_major <<
				", Minor = " << compiler_options->frontend_version_minor <<
				", Build = " << compiler_options->frontend_version_build <<
				", QFE = " << compiler_options->frontend_version_qfe << '\n';
			std::cout << "\tBackend Version: Major = " << compiler_options->backend_version_major <<
				", Minor = " << compiler_options->backend_version_minor <<
				", Build = " << compiler_options->backend_version_build <<
				", QFE = " << compiler_options->backend_version_qfe << '\n';
			std::cout << "\tVersion string: " << compiler_options->version_string << '\n';
		}
		break;

	case 0x114c: // S_BUILDINFO
		{
			assert(data.size() == sizeof(std::uint32_t));
			const auto build_id = *reinterpret_cast<const std::uint32_t*>(data.data());
			std::cout << "S_BUILDINFO: 0x" << std::hex << build_id << '\n';
		}
		break;

		case 0x1124: // S_UNAMESPACE - using namespace
		{
			const std::string_view name(reinterpret_cast<const char*>(data.data()), data.size());
			std::cout << "S_UNAMESPACE: " << name << '\n';
		}
		break;
	}
}

void dump_symbols(std::span<const unsigned char> data)
{
	while (!data.empty())
	{
		assert(data.size() >= sizeof(coff::Symbol_record));
		const auto record = reinterpret_cast<const coff::Symbol_record*>(data.data());
		data = data.subspan(sizeof(coff::Symbol_record));
		assert(data.size() >= record->length - 2);
		dump_symbol(record, data.first(record->length - 2));
		data = data.subspan(record->length - 2);
	}
}

void dump_file_checksums(std::span<const unsigned char> data)
{
#pragma pack(push, 1)
	struct File_data {
		std::uint32_t offset_file_name;
		std::uint8_t cb_checksum;
		std::uint8_t checksum_type;
	} file_data;
#pragma pack(pop)

	std::cout << "FileId  St.Offset  Cb  Type  ChcksumBytes\n";
	std::uint32_t file_id = 0; // TODO: how is this actually calculated?

	while (!data.empty())
	{
		assert(data.size() >= sizeof(File_data));
		const auto file_data = reinterpret_cast<const File_data*>(data.data());
		data = data.subspan(sizeof(*file_data));
		assert(data.size() >= file_data->cb_checksum);
		const std::span<const unsigned char> checksum = data.first(file_data->cb_checksum);
		data = data.subspan(file_data->cb_checksum);
		std::cout << file_id << ' ' << file_data->offset_file_name << ' ';
		switch (file_data->checksum_type)
		{
		case 0x0: // CHKSUM_TYPE_NONE
			{
			}
			break;

		case 0x1: // CHKSUM_TYPE_MD5
			{
			}
			break;

		case 0x2: // CHKSUM_TYPE_SHA1
			{
			}
			break;

		case 0x3: // CHKSUM_TYPE_SHA256
			{
				std::cout << "SHA_256" << ' ';
			}
			break;

		default: // Unknown
			{
				std::cout << static_cast<std::uint32_t>(file_data->checksum_type) << '\n';
			}
			break;
		}

		for (std::size_t i = 0; i < checksum.size(); ++i)
		{
			std::cout << std::setfill('0') << std::setw(2) << std::hex << static_cast<std::uint32_t>(checksum[i]);
		}
		std::cout << std::endl;

		// Next file checksum starts on a 4-byte boundary
		const std::size_t remainder = (sizeof(*file_data) + file_data->cb_checksum) % 4;
		if (remainder != 0)
		{
			data = data.subspan(4 - remainder);
		}
	}
}

void dump_string_table(std::span<const unsigned char> data)
{
	std::uint32_t index = 0;
	auto iter = data.begin();
	while (iter != data.end())
	{
		std::cout << index << ' ';
		auto end_of_string = std::find(iter, data.end(), '\0');
		assert(iter != data.end());
		const std::string_view value(reinterpret_cast<const char*>(&*iter), end_of_string - iter);
		std::cout << value << '\n';
		++end_of_string;
		iter = end_of_string;
		++index;
	}
}

void dump_type(const std::uint16_t kind, std::span<const unsigned char> type_data)
{
	// See include/cvinfo.h in microsoft-pdb repository
	switch (kind)
	{
	case 0x1001: // LF_MODIFIER
		{
			std::cout << "LF_MODIFIER\n";
			const auto result = parse<code_view::Modifier>(type_data);
			assert(result.first);
			std::cout << result.first->attributes << ", modifies type " << result.first->type << '\n';
		}
		break;

	case 0x1002: // LF_POINTER
		{
			std::cout << "LF_POINTER\n";
			const auto result = parse<code_view::Pointer>(type_data);
			assert(result.first);
			std::cout << "Element type: " << result.first->type << '\n';
		}
		break;

	case 0x1008: // LF_PROCEDURE
		{
			std::cout << "LF_PROCEDURE\n";
			const auto result = parse<code_view::Procedure>(type_data);
			const auto procedure = result.first;
			std::cout << "Return type = " << procedure->return_type << ", Call type = " << (std::uint32_t)procedure->calling_convention << '\n';
			std::cout << "Func attr = " << (std::uint32_t)procedure->attributes << '\n';
			std::cout << "# Params = " << procedure->parameter_count << ", Arg list type = " << procedure->arg_list << '\n';
		}
		break;

	case 0x1201: // LF_ARGLIST
		{
			std::cout << "LF_ARGLIST";
			const auto result = parse<code_view::Argument_list>(type_data);
			const auto argument_list = result.first;
			std::cout << " argument count " << argument_list->count << '\n';
			assert(result.second.size() >= argument_list->count * sizeof(std::uint32_t));
			const auto types = reinterpret_cast<const std::uint32_t*>(result.second.data());
			for (std::uint32_t i = 0; i < argument_list->count; ++i)
			{
				std::cout << "list[" << i << "] = " << types[i] << '\n';
			}
		}
		break;

	case 0x1203: // LF_FIELDLIST
		{
			std::cout << "LF_FIELDLIST\n";
			assert(type_data.size() >= sizeof(std::uint16_t));
			type_data = type_data.subspan(sizeof(std::uint16_t));
			while (type_data.size() >= sizeof(code_view::Member))
			{
				const auto member = parse<code_view::Member>(type_data);
				assert(member.first);
				const auto name = parse_string(member.second);
				std::cout << name.first << ' ' << member.first->index << '\n';
				type_data = name.second;
			}
		}
		break;

	case 0x1505: // LF_STRUCTURE
		{
			std::cout << "LF_STRUCTURE\n";
			const auto structure = parse<code_view::Structure>(type_data);
			assert(structure.first);
			std::cout << "Size = 0";
			const auto name = parse_string(structure.second);
			std::cout << ", class name = " << name.first;
			if (structure.first->properties.has_unique_name)
			{
				const auto unique_name = parse_string(name.second);
				std::cout << ", unique name = " << unique_name.first;
			}
			std::cout << '\n';
		}
		break;

	case 0x1601: // LF_FUNC_ID
		{
			std::cout << "LF_FUNC_ID\n";
			const auto result = parse<code_view::Func_id>(type_data);
			const auto func_id = result.first;
			const auto name = parse_string(result.second);
			std::cout << "Type = " << func_id->type << " Scope = " << func_id->scope_id << ' ' << name.first << '\n';
		}
		break;

	case 0x1603: // LF_BUILDINFO
		{
			std::cout << "LF_BUILDINFO\n";
			const auto result = parse<code_view::Build_info>(type_data);
			std::cout << "String ID's (count = " << result.first->count << "):";
			assert(result.second.size() >= result.first->count * sizeof(std::uint32_t));
			const auto args = reinterpret_cast<const std::uint32_t*>(result.second.data());
			for (std::uint32_t i = 0; i < result.first->count; ++i)
			{
				std::cout << ' ' << args[i];
			}
			std::cout << '\n';
		}
		break;

	case 0x1604: // LF_SUBSTR_LIST
		{
			std::cout << "LF_SUBSTR_LIST\n";
			const auto result = parse<code_view::Argument_list>(type_data);
			const auto substr_list = result.first;
			std::cout << "String ID's (count = " << substr_list->count << "):";
			assert(result.second.size() >= substr_list->count * sizeof(std::uint32_t));
			const auto string_ids = reinterpret_cast<const std::uint32_t*>(result.second.data());
			for (std::uint32_t i = 0; i < substr_list->count; ++i)
			{
				std::cout << ' ' << string_ids[i];
			}
			std::cout << '\n';
		}
		break;

	case 0x1605: // LF_STRING_ID
		{
			std::cout << "LF_STRING_ID\n";
			const auto result = parse<code_view::String_id>(type_data);
			assert(result.first);
			const auto name = parse_string(result.second);
			std::cout << name.first << '\n';
		}
		break;

	case 0x1606: // LF_UDT_SRC_LINE
		{
			std::cout << "LF_UDT_SRC_LINE\n";
			const auto result = parse<code_view::Udt_src_line>(type_data);
			assert(result.first);
			std::cout << "type = " << result.first->type << ", source file = " << result.first->source << ", line = " << result.first->line_number << '\n';
		}
		break;

	default:
		{
			std::cout << "(unrecognised)" << '\n';
		}
		break;
	}
}

int main(int argc, char** argv)
{
	std::ifstream object_file(argv[1], std::ios::binary);
	const std::vector<unsigned char> obj(std::istreambuf_iterator<char>(object_file), {});
	const unsigned char* ptr = obj.data();
	const auto header = reinterpret_cast<const coff::File_header*>(ptr);
	ptr += sizeof(*header);
	auto section = reinterpret_cast<const coff::Section_header*>(ptr);

	const unsigned char* const string_table = obj.data() + header->symbol_table_ptr + header->number_of_symbols * sizeof(coff::Symbol);
	const std::uint32_t string_table_size = *reinterpret_cast<const std::uint32_t*>(string_table);
	const std::string_view string_table_sv(reinterpret_cast<const char*>(string_table + 4), string_table_size);

	for (std::uint16_t i = 0; i < header->number_of_sections; ++i)
	{
		std::cout << section->name << '\n';
		if (std::strcmp(section->name, ".drectve") == 0)
		{
			const auto data = reinterpret_cast<const char*>(obj.data() + section->data_offset);
			std::string_view sv(data, section->size_in_bytes);
			std::cout << '\'' << sv << "'\n";
		}
		else if (std::strcmp(section->name, ".chks64") == 0)
		{
			const auto data = reinterpret_cast<const unsigned char*>(obj.data() + section->data_offset);
			const std::span<const unsigned char> span(data, section->size_in_bytes);
			// TODO: Not sure how to parse this???
		}
		else if (std::strcmp(section->name, ".debug$S") == 0)
		{
			// CodeView symbol records
			const std::uint32_t signature = *reinterpret_cast<const std::uint32_t*>(obj.data() + section->data_offset);
			assert(signature == 0x4); // CV_SIGNATURE_C13
			std::uint32_t bytes_read = sizeof(signature);
			while (bytes_read < section->size_in_bytes)
			{
				// Round up to next multiple of 4
				if ((bytes_read & 3) != 0)
				{
					bytes_read += 4 - (bytes_read & 3);
				}

				if (bytes_read == section->size_in_bytes)
				{
					break;
				}

				const std::uint32_t sst = *reinterpret_cast<const std::uint32_t*>(obj.data() + section->data_offset + bytes_read);
				bytes_read += 4;
				std::uint32_t cb = *reinterpret_cast<const std::uint32_t*>(obj.data() + section->data_offset + bytes_read);
				bytes_read += 4;

				if (cb == 0)
				{
					cb = section->size_in_bytes - bytes_read;
				}

				const std::span<const unsigned char> subsection(obj.data() + section->data_offset + bytes_read, cb);

				switch (sst)
				{
				case 0xf1: // DEBUG_S_SYMBOLS
					{
						// DumpModSymC7: cvdump.cpp:1731
						std::cout << "*** Symbols\n\n";
						dump_symbols(subsection);
					}
					break;
				case 0xf3: // DEBUG_S_STRINGTABLE
					{
						std::cout << "*** String table\n\n";
						dump_string_table(subsection);
					}
					break;
				case 0xf4: // DEBUG_S_FILECHKSMS
					{
						// DumpModFileChecksums: dumpsym7.cpp:1095
						dump_file_checksums(subsection);
					}
					break;
				}

				bytes_read += cb;
			}
		}
		else if (std::strcmp(section->name, ".debug$T") == 0)
		{
			std::span<const unsigned char> code_view_data(obj.data() + section->data_offset, section->size_in_bytes);
			const std::span<const unsigned char> signature(code_view_data.data(), sizeof(std::uint32_t));
			code_view_data = code_view_data.subspan(sizeof(std::uint32_t));
			std::uint16_t base = 0x1000;
			while (!code_view_data.empty())
			{
				const auto length = parse<std::uint16_t>(code_view_data);
				code_view_data = length.second;
				const auto kind = parse<std::uint16_t>(code_view_data);
				const std::span<const std::uint8_t> type_data = code_view_data.first(*length.first);
				std::cout << "0x" << std::setw(4) << std::setfill('0') << std::hex << base;
				std::cout << " : Length = " << std::dec << *length.first << ", Leaf = ";
				std::cout << "0x" << std::setw(4) << std::setfill('0') << std::hex << *kind.first << ' ';
				dump_type(*kind.first, type_data);
				std::cout << std::endl;
				++base;
				code_view_data = code_view_data.subspan(*length.first);
			}
		}
		++section;
	}

	// Symbol table
	const std::span<const coff::Symbol> symbol_table(reinterpret_cast<const coff::Symbol*>(obj.data() + header->symbol_table_ptr), header->number_of_symbols);
	std::cout << "Symbol table:\n";
	std::int32_t symbol_index = 0;
	while (symbol_index < symbol_table.size())
	{
		/* std::cout << symbol_table[symbol_index].name << '\n'; */
		std::cout << get_name(symbol_table[symbol_index].name, string_table_sv) << '\n';
		assert(symbol_index + symbol_table[symbol_index].number_of_aux_symbols < symbol_table.size());
		const std::int32_t number_of_aux_symbols = symbol_table[symbol_index].number_of_aux_symbols;
		for (std::int32_t aux_index = 0; aux_index < number_of_aux_symbols; ++aux_index)
		{
			//std::cout << symbol_table[symbol_index + aux_index].name << '\n';
		}
		symbol_index += number_of_aux_symbols + 1;
	}
}
